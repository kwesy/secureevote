from payments.models.withdrawal_transaction import WithdrawalTransaction
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

class WithdrawalTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalTransaction
        fields = [
            'id', 'amount', 'status', 'withdraw_method', 'provider', 'phone_number', 'payment_reference', 'created_at',
        ]
        read_only_fields = ['payment_reference', 'status', 'created_at']

class WithdrawalTransactionOTPSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=40)
    code = serializers.CharField(min_length=6 , max_length=6)
    class Meta:
        model = None
        fields = [
            'id', 'code'    # transaction ID and OTP code for verification
        ]

class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = ['id', 'event_id', 'candidate_id', 'payload', 'is_valid', 'received_at']
