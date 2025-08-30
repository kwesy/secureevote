from django.urls import path
from .views import InitiateVoteView, HubtelWebhookView, ResendOTPView, TicketPaymentView, VoteTransactionHistoryView, WithdrawalOTPConfirmationView, WithdrawalTransactionView

app_name = "payments"

urlpatterns = [
    path('vote', InitiateVoteView.as_view(), name='initiate-vote'),
    path('vote/transactions', VoteTransactionHistoryView.as_view(), name='vote-transactions'),
    path('withdrawals', WithdrawalTransactionView.as_view(), name='withdrawals'),
    path('withdrawals/verify-otp', WithdrawalOTPConfirmationView.as_view(), name='withdrawal-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),

    #ticket purchase
    path('tickets', TicketPaymentView.as_view(), name='purchase-ticket'),
]

# Hubtel Webhook URL
urlpatterns += [
    path('webhook', HubtelWebhookView.as_view(), name='hubtel-webhook'),
]