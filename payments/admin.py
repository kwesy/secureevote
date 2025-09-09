from django.contrib import admin
from core.models.vote import VoteTransaction
from .models.webhook_log import WebhookLog

@admin.register(VoteTransaction)
class VoteTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vote_count', 'candidate', 'is_verified')
    list_filter = ('is_verified', 'candidate')
    search_fields = ('candidate',)
    raw_id_fields = ('candidate',)

@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'instance_id', 'is_valid', 'created_at', 'updated_at')
    list_filter = ('is_valid',)
    readonly_fields = ('payload',)
