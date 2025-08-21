from rest_framework import serializers
from .models.vote_transaction import VoteTransaction
from .models.webhook_log import WebhookLog

class VoteTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteTransaction
        fields = [
            'id', 'candidate', 'vote_count',
            'amount', 'status', 'payment_method', 'provider', 'phone_number', 'payment_reference', 'is_verified', 'created_at'
        ]
        read_only_fields = ['payment_reference', 'event', 'category', 'is_verified', 'created_at']

class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = ['id', 'event_id', 'candidate_id', 'payload', 'is_valid', 'received_at']
