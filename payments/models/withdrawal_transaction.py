import uuid
from django.db import models
from core.models.category import Category
from core.models.event import Event
from core.models.candidate import Candidate
from core.models.common import TimeStampedModel

class WithdrawalTransaction(TimeStampedModel):
    PAYMENT_METHOD_CHOICES = [('momo', 'Mobile Money'), ('card', 'Card'), ('bank', 'Bank')]
    PROVIDER_CHOICES = [('mtn', 'MTN'), ('airtel', 'Airtel'), ('telecel', 'Telecel')]
    PAYMENT_STATUS_CHOICES = [('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    withdraw_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    payment_reference = models.CharField(max_length=100, unique=True, null=True)
    status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS_CHOICES)
    otp = models.ForeignKey('core.OTP', on_delete=models.CASCADE, related_name='withdrawals')
    is_verified = models.BooleanField(default=False)
