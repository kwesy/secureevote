import uuid
from django.db import models
from core.models.category import Category
from core.models.event import Event
from core.models.candidate import Candidate
from core.models.common import TimeStampedModel

class Transaction(TimeStampedModel):
    PAYMENT_METHOD_CHOICES = [('momo', 'Mobile Money'), ('card', 'Card'), ('bank', 'Bank')]
    PROVIDER_CHOICES = [('mtn', 'MTN'), ('airtel', 'Airtel'), ('telecel', 'Telecel')]
    PAYMENT_STATUS_CHOICES = [('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')]
    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'Payment'),         # Customer pays for a product/service
        ('refund', 'Refund'),           # Refund to customer
        ('withdrawal', 'Withdrawal'),   # Payout from platform to user
        ('deposit', 'Deposit'),         # Money added to user account
        ('transfer', 'Transfer'),       # Between accounts
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    external_payment_id = models.CharField(max_length=100, unique=True, null=True)
    currency = models.CharField(max_length=10, default='GHS')  # or use choices
    status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS_CHOICES)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    desc = models.TextField(blank=True, null=True)
    # fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # customer_name = models.CharField(max_length=100, blank=True,
    # metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Tx: {self.id[:5]} - {self.amount} votes"
