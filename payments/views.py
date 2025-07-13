import uuid
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models.candidate import Candidate
from .models.vote_transaction import VoteTransaction
from .serializers import VoteTransactionSerializer
from .services.hubtel import initiate_payment

class InitiateVoteView(APIView):
    permission_classes = []

    def post(self, request):
        candidate_id = request.data.get('candidate_id')
        vote_count = int(request.data.get('vote_count', 0))
        customer_number = request.data.get('phone')

        if vote_count <= 0 or not customer_number:
            return Response({'detail': 'Invalid input'}, status=400)

        candidate = Candidate.objects.select_related('event').filter(id=candidate_id, is_blocked=False).first()
        if not candidate:
            return Response({'detail': 'Candidate not found'}, status=404)

        amount = candidate.event.amount_per_vote * Decimal(vote_count)
        reference = str(uuid.uuid4())

        tx = VoteTransaction.objects.create(
            event=candidate.event,
            candidate=candidate,
            vote_count=vote_count,
            amount_paid=amount,
            payment_reference=reference,
        )

        description = f"{vote_count} votes for {candidate.name} ({candidate.event.name})"
        payment_response = initiate_payment(reference, amount, description, customer_number)

        return Response({
            "payment_url": payment_response.get("checkoutUrl"),
            "reference": reference,
            "amount": str(amount),
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
