import uuid
from decimal import Decimal
from core.models.candidate import Candidate
from core.models.otp import OTP, generate_secure_otp
from core.serializers import OTPSerializer, ResendOTPSerializer
from payments.models.transaction import Transaction
from core.models.withdrawal import WithdrawalTransaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import APIException, ValidationError, PermissionDenied
from core.models.vote import VoteTransaction
from services.services import charge_mobile_money, send_email
from .serializers import TicketTransactionSerializer, VoteTransactionSerializer, WithdrawalTransactionSerializer
from .services.hubtel import initiate_payment
from core.mixins.response import StandardResponseView
from core.permissions import IsOrganizer
from django.shortcuts import get_object_or_404
import hmac, hashlib, json, logging
from decouple import config
from django.db import models
from ipware import get_client_ip


PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')
PAYSTACK_IPS = config('ALLOWED_PAYSTACK_IPS', cast=lambda v: [ip.strip() for ip in v.split(',')])

logger = logging.getLogger("paystack")
error_logger = logging.getLogger("error")

class InitiateVoteView(StandardResponseView):
    permission_classes = []
    serializer_class = VoteTransactionSerializer
    success_message = "transaction initiated successfully"

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data.pop('phone_number')
        channel = serializer.validated_data.pop('channel')
        provider = serializer.validated_data.pop('provider')

        vote_count = serializer.validated_data.get('vote_count')
        candidate = serializer.validated_data.get('candidate')

        if vote_count <= 0 or not phone_number:
            return Response({'detail': 'Invalid input'}, status=400)

        if not candidate:
            return Response({'detail': 'Candidate not found'}, status=404)

        try:
            amount = abs(candidate.event.amount_per_vote * int(vote_count))

            # Create transaction object
            payment = Transaction.objects.create(
                amount=amount,
                channel=channel,
                provider=provider,
                phone_number=phone_number,
                status='pending',
                currency='GHS',
                type='payment',
                desc=f"{vote_count} votes for {candidate.name} ({candidate.event.name})",
                gateway='paystack',
            )

            # Save vote record with payment linked
            instance = serializer.save(payment=payment)

            if channel == 'momo':
                payment_response = charge_mobile_money(amount, phone_number, provider, metadata={"p":0, "id": str(instance.id)})    # p = 0 for vote payment, id = vote transaction id
                payment.external_payment_id = payment_response.get('data')['id']
                payment.save()
            else:
                raise ValidationError("Unsupported payment channel this resource.")

        except Exception as e:
            # If it's a DRF exception, raise it again without altering
            if isinstance(e, (APIException, ValidationError)):
                raise e
            
            error_logger.error('Error creating transaction: %s', str(e), exc_info=True)
            return APIException({'detail': 'Transaction Failed!'}, status=500)


        return Response({
            "status": payment_response["data"]["status"],
            "amount": payment_response["data"]["amount"]/100,  # Convert from pesewa to GHS
            "reference": payment_response["data"]["reference"],
            "channel": payment_response["data"]["channel"],
            "phone_number": payment_response["data"]["authorization"]["mobile_money_number"],
            "provider": payment_response["data"]["authorization"]["bank"],
            "candidate": {
                "id": instance.candidate.id,
                "name": instance.candidate.name,
                },
            "vote": instance.vote_count,
            "completed_at": payment_response["data"]["paid_at"]
        })

# Hubtel Webhook View
from .models.webhook_log import WebhookLog
from django.db import transaction

class HubtelWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        payload = request.data
        reference = payload.get("ClientReference")
        status_code = payload.get("Status")

        log = WebhookLog.objects.create(
            event_id=payload.get("Data", {}).get("EventId", ""),
            candidate_id=payload.get("Data", {}).get("CandidateId", ""),
            payload=payload,
            is_valid=False,
        )

        if not reference or status_code != "Success":
            return Response({"detail": "Invalid or failed payment"}, status=400)

        try:
            with transaction.atomic():
                tx = VoteTransaction.objects.select_for_update().get(payment_reference=reference, is_verified=False)
                tx.is_verified = True
                tx.save()

                candidate = tx.candidate
                candidate.vote_count = models.F("vote_count") + tx.vote_count
                candidate.save(update_fields=['vote_count'])

                log.is_valid = True
                log.save()
        except VoteTransaction.DoesNotExist:
            return Response({"detail": "Transaction not found or already verified"}, status=400)

        return Response({"detail": "Payment confirmed"}, status=200)

class PaystackWebhookView(APIView):
    authentication_classes = []  # public
    permission_classes = []      # public

    def initial(self, request, *args, **kwargs):
        ip, is_routable = get_client_ip(request)
        if not ip or ip not in PAYSTACK_IPS:
            logger.warning(f"Blocked IP: {ip}")
            raise PermissionDenied("Forbidden")
        super().initial(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        raw_body = request.body.decode("utf-8")
        signature = request.headers.get("X-Paystack-Signature")

        payload = json.loads(raw_body)
        event = payload.get("event", "")
        amount = payload.get("data", {}).get("amount", 0)
        payment_status = payload.get("data", {}).get("status", None)
        ext_payment_id = payload.get("data", {}).get("id", None)
        metadata = payload.get("data", {}).get("metadata", {})
        product = -1
        instance_id = ""

        if isinstance(metadata, dict):
            product = int(metadata.get("p", -1))  # p = 0 for vote, 1 for ticket, -1 unknown
            instance_id = str(metadata.get("id", ""))
        else:
            # fallback: stringify entire metadata if it's not a dict
            metadata = str(metadata)
            instance_id = metadata

        # Verify signature
        expected_signature = hmac.new(
            PAYSTACK_SECRET_KEY.encode("utf-8"),
            raw_body.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid signature, event: {%s}, external_payment_id: {%s}", event, ext_payment_id)
            raise PermissionDenied("Invalid signature")

        # Save raw log
        WebhookLog.objects.create(
            event=event, 
            product=product,  # 0 for vote, 1 for ticket, -1 unknown
            instance_id=instance_id, # vote or ticket transaction id 
            payload=raw_body,
            is_valid=True
        )

        if event == 'charge.success':
            try:
                with transaction.atomic():
                    tx = Transaction.objects.select_for_update().get(external_payment_id=ext_payment_id, gateway="paystack")

                    # Check for underpayment
                    if Decimal(amount) / 100 < tx.amount:
                        logger.error("Amount underpaid for transaction %s: expected %s, got %s", tx.id, tx.amount, Decimal(amount)/100)
                        
                    # Update transaction status
                    tx.status = payment_status
                    tx.save()

                    # Process based on product type
                    if product == 0 and payment_status == "success":  # p = 0 for vote payment
                        vote_tx = VoteTransaction.objects.select_for_update().get(id=instance_id, is_verified=False)
                        vote_tx.is_verified = True
                        vote_tx.save()
                        # Update candidate vote_count atomically
                        Candidate.objects.filter(id=vote_tx.candidate.id).update(
                            vote_count=models.F("vote_count") + vote_tx.vote_count
                        )
                    elif product == 1:  # p = 1 for ticket payment
                        #TODO: For ticket payments, implement ticket delivery logic here
                        pass
                    else:
                        logger.error("Unknown product type in metadata: %s", metadata.get("p"))

            except Transaction.DoesNotExist:
                logger.error("Transaction not found for external_payment_id: %s", ext_payment_id)
                return Response({"detail": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
            except VoteTransaction.DoesNotExist:
                logger.error("VoteTransaction not found or already verified for id: %s", metadata.get("id"))
                return Response({}, status=status.HTTP_202_OK) # Already processed, return 200 since payment was successful
            except Exception as e:
                logger.error("Error processing webhook for external_payment_id %s: %s", ext_payment_id, str(e))
                raise APIException("Error processing webhook for external_payment_id: %s", ext_payment_id)

            return Response(status=status.HTTP_200_OK)
        
        logger.info("Unhandled event type: %s", event)
        return Response(status=status.HTTP_200_OK)

# Vote Transactions History View 
class VoteTransactionHistoryView(StandardResponseView, generics.ListAPIView):
    permission_classes = [IsOrganizer]

    def get(self, request):
        user = request.user

        transactions = VoteTransaction.objects.filter(candidate__event__user=user).order_by('-created_at')
        serializer = VoteTransactionSerializer(transactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

# Withdrawal Transactions History View
class WithdrawalTransactionView(StandardResponseView, generics.ListAPIView, generics.CreateAPIView):
    serializer_class = WithdrawalTransactionSerializer
    permission_classes = [IsOrganizer]

    def get(self, request):
        user = request.user

        transactions = WithdrawalTransaction.objects.filter(user=user, is_verified=True).order_by('-created_at')
        serializer = WithdrawalTransactionSerializer(transactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        self.success_message = "Withdrawal transaction created successfully"
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        channel = serializer.validated_data.pop('channel')
        provider = serializer.validated_data.pop('provider')
        phone_number = serializer.validated_data.pop('phone_number')
        # Ensure the user has a valid wallet balance
        #TODO: permissions eg. minimum balance, max withdrawal limit, is_withdrawal_allowed, etc.
        if request.user.balance >= serializer.validated_data['amount']:
            # Create the withdrawal transaction and otp
            otp = OTP.objects.create(is_verified=False)
            transaction = Transaction.objects.create(
                amount=serializer.validated_data['amount'],
                channel=channel,
                provider=provider,
                phone_number=phone_number,
                status='pending',
                currency='GHS',
                type='withdrawal',
                desc=f"Withdrawal of {serializer.validated_data['amount']} GHS via {channel}",
            )
            serializer.save(otp=otp, user=request.user, transaction=transaction)

            try:
                send_email(
                    subject="Confirm Your Withdrawal - SecureEVote",
                    template_name="emails/withdraw_request_confirmation.html",
                    context={
                        "organizer_name": request.user.organization_name,
                        "amount": f"₵{serializer.validated_data['amount']}",
                        "payout_method": f"{provider} {serializer.get_channel_display} ({phone_number})",
                        "otp": otp.code,
                        "expiry_minutes": 5,
                        "year": 2025,
                    },
                    recipient_list=[request.user.email],
                )
            except Exception as e:
                logger.error(f"Error sending email: {e}", exc_info=True)
                raise e

        else:
            return Response({'detail': 'Insufficient balance for withdrawal'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Withdrawal OTP confirmation view
class WithdrawalOTPConfirmationView(StandardResponseView, generics.CreateAPIView):
    serializer_class = OTPSerializer
    permission_classes = [IsOrganizer]

    def post(self, request):
        self.success_message = "OTP confirmed successfully"
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        withdrawal_id = serializer.validated_data.get('id')
        code = serializer.validated_data.get('code')

        try:
            withdrawal = WithdrawalTransaction.objects.get(id=withdrawal_id, user=request.user)

            # Verify the OTP code
            if withdrawal and not withdrawal.is_verified and withdrawal.otp.verify(code):
                request.user.balance -= withdrawal.transaction.amount
                withdrawal.is_verified = True
                request.user.save()
                withdrawal.save()
                #TODO: send money to user
                return Response({"detail": "OTP confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid OTP code or Expired"}, status=status.HTTP_400_BAD_REQUEST)
            
        except WithdrawalTransaction.DoesNotExist:
            return Response({"detail": "Withdrawal transaction not found"}, status=status.HTTP_404_NOT_FOUND)

#OTP Resend View
class ResendOTPView(StandardResponseView):
    permission_classes = [IsOrganizer]
    serializer_class = ResendOTPSerializer

    def post(self, request):
        self.success_message = "OTP resent successfully."
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        request_id = serializer.validated_data.get('id')
        otp = get_object_or_404(OTP, request_id=request_id, is_verified=False, )
        otp.code = generate_secure_otp(6)
        otp.save()

        #TODO: Integrate with SMS service to send the OTP code to the user's email or phone number
        return Response(None, status=status.HTTP_201_CREATED)

# Ticket Payment View
class TicketPaymentView(StandardResponseView):
    permission_classes = []
    serializer_class = TicketTransactionSerializer
    success_message = "transaction initiated successfully"

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data.pop('phone_number')
        channel = serializer.validated_data.pop('channel')
        provider = serializer.validated_data.pop('provider')

        ticket = serializer.validated_data.get('ticket')

        try:
            amount = ticket.price
            payment = Transaction.objects.create(
                amount=amount,
                channel=channel,
                provider=provider,
                phone_number=phone_number,
                status='pending',
                currency='GHS',
                type='payment',
                desc=f"Payment for ticket {ticket.type} ({ticket.event.name})",
            )

            instance = serializer.save(payment=payment)

            description = f"Payment for ticket {ticket.type} ({ticket.event.name})"
            payment_response = initiate_payment('refrence', amount, description, phone_number)

        except Exception as e:
            print(f"Error creating transaction: {e}")
            return Response({'detail': 'Failed to create transaction'}, status=500)

        return Response({
            "payment_url": payment_response.get("checkoutUrl"),
            "reference": instance.id,
            "amount": instance.payment.amount,
        })
    