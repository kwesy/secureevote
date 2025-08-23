from django.urls import path
from .views import InitiateVoteView, HubtelWebhookView, VoteTransactionHistoryView, WithdrawalTransactionHistoryView

app_name = "payments"

urlpatterns = [
    path('vote', InitiateVoteView.as_view(), name='initiate-vote'),
    path('vote/transactions', VoteTransactionHistoryView.as_view(), name='vote-transactions'),
    path('withdrawals', WithdrawalTransactionHistoryView.as_view(), name='withdrawals'),
]

# Hubtel Webhook URL
urlpatterns += [
    path('webhook', HubtelWebhookView.as_view(), name='hubtel-webhook'),
]