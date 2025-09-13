from core.models.ticket import TicketSale
from payments.models.transaction import PAYMENT_METHOD_CHOICES, PROVIDER_CHOICES
from core.models.withdrawal import WithdrawalTransaction
from rest_framework import serializers
from core.models.vote import VoteTransaction
from .models.webhook_log import WebhookLog

class VoteTransactionSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, write_only=True, required=True)
    channel = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, write_only=True, required=True)
    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES, write_only=True, required=True)

    @property
    def get_channel_display(self):
        return dict(PAYMENT_METHOD_CHOICES).get(self.validated_data.get('payment_method'))

    class Meta:
        model = VoteTransaction
        fields = [
            'id', 'candidate', 'vote_count', 'payment', 'is_verified',
            'provider', 'phone_number', 'channel',  # payment details
        ]
        read_only_fields = ['id', 'is_verified', 'payment']

class WithdrawalTransactionSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, write_only=True, required=True)
    channel = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, write_only=True, required=True)
    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES, write_only=True, required=True)

    @property
    def get_channel_display(self):
        return dict(PAYMENT_METHOD_CHOICES).get(self.validated_data.get('channel'))

    class Meta:
        model = WithdrawalTransaction
        fields = [
            'id', 'amount', 'transaction', 
            'phone_number', 'channel', 'provider', # payment details
            ]
        read_only_fields = ['id', 'transaction']

class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = ['id', 'event_id', 'candidate_id', 'payload', 'is_valid', 'received_at']

class TicketTransactionSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, write_only=True, required=True)
    channel = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, write_only=True, required=True)
    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES, write_only=True, required=True)

    class Meta:
        model = TicketSale
        fields = ['id', 'ticket', 'recipient_name', 'recipient_contact', 'recipient_email', 
                  'phone_number', 'channel', 'provider',] # payment details
        read_only_fields = ['id', 'created_at', 'payment']
