from django.urls import path
from .views import InitiateVoteView, HubtelWebhookView

app_name = "payments"

urlpatterns = [
    path('vote', InitiateVoteView.as_view(), name='initiate-vote'),
]

# Hubtel Webhook URL
urlpatterns += [
    path('webhook', HubtelWebhookView.as_view(), name='hubtel-webhook'),
]