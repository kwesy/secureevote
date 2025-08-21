from django.contrib import admin
from .models.vote_transaction import VoteTransaction
from .models.webhook_log import WebhookLog

@admin.register(VoteTransaction)
class VoteTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'vote_count', 'amount', 'phone_number', 'payment_method', 'provider', 'candidate', 'category', 'event', 'status', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('payment_reference',)
    raw_id_fields = ('event', 'candidate')

@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_id', 'candidate_id', 'is_valid', 'received_at')
    list_filter = ('is_valid',)
    readonly_fields = ('payload',)
