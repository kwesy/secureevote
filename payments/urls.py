from django.urls import path
from .views import InitiateVoteView, HubtelWebhookView, PaystackWebhookView, ResendOTPView, TicketPaymentView, VoteTransactionHistoryView, WithdrawalOTPConfirmationView, WithdrawalTransactionView

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

#Webhook URL
urlpatterns += [
    path('webhooks/hubtel', HubtelWebhookView.as_view(), name='hubtel-webhook'),
    path('webhooks/paystack', PaystackWebhookView.as_view(), name="paystack-webhook"),
]
