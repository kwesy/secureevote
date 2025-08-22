from django.urls import path
from .views import InitiateVoteView, HubtelWebhookView, VoteTransactionHistoryView

app_name = "payments"

urlpatterns = [
    path('vote', InitiateVoteView.as_view(), name='initiate-vote'),
    path('vote/transactions', VoteTransactionHistoryView.as_view(), name='vote-transactions'),
]

# Hubtel Webhook URL
urlpatterns += [
    path('webhook', HubtelWebhookView.as_view(), name='hubtel-webhook'),
]