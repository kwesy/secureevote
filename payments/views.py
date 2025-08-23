import uuid
from decimal import Decimal
from core.models.otp import OTP
from payments.models.withdrawal_transaction import WithdrawalTransaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from core.models.candidate import Candidate
from .models.vote_transaction import VoteTransaction
from .serializers import VoteTransactionSerializer, WithdrawalTransactionOTPSerializer, WithdrawalTransactionSerializer
from .services.hubtel import initiate_payment
from core.mixins.response import StandardResponseView
from core.permissions import IsOrganizer

class InitiateVoteView(StandardResponseView):
    permission_classes = []
    serializer_class = VoteTransactionSerializer
    success_message = "transaction initiated successfully"

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data.get('phone_number')
        vote_count = serializer.validated_data.get('vote_count')
        candidate = serializer.validated_data.get('candidate')

        print(f"Received vote request: candidate_id={candidate}, vote_count={vote_count}, phone_number={phone_number}")

        if vote_count <= 0 or not phone_number:
            return Response({'detail': 'Invalid input'}, status=400)

        if not candidate:
            return Response({'detail': 'Candidate not found'}, status=404)
        
        try:
            amount = candidate.event.amount_per_vote * Decimal(vote_count)

            instance = serializer.save(amount=amount)

            description = f"{vote_count} votes for {candidate.name} ({candidate.event.name})"
            payment_response = initiate_payment(id, amount, description, phone_number)

        except Exception as e:
            print(f"Error creating transaction: {e}")
            return Response({'detail': 'Failed to create transaction'}, status=500)

        return Response({
            "payment_url": payment_response.get("checkoutUrl"),
            "reference": instance.id,
            "amount": instance.amount,
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
        
        # Ensure the user has a valid wallet balance
        if request.user.balance >= serializer.validated_data['amount']:
            # Create the withdrawal transaction and otp
            otp = OTP.objects.create(is_verified=False)
            serializer.save(otp=otp, user=request.user)
        else:
            return Response({'detail': 'Insufficient balance for withdrawal'}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Withdrawal OTP confirmation view
class WithdrawalOTPConfirmationView(StandardResponseView, generics.CreateAPIView):
    serializer_class = WithdrawalTransactionOTPSerializer
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
                request.user.balance -= withdrawal.amount
                withdrawal.is_verified = True
                request.user.save()
                withdrawal.save()
                #TODO: send money to user
                return Response({"detail": "OTP confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid OTP code"}, status=status.HTTP_400_BAD_REQUEST)
            
        except WithdrawalTransaction.DoesNotExist:
            return Response({"detail": "Withdrawal transaction not found"}, status=status.HTTP_404_NOT_FOUND)
