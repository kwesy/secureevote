from django.db import models
from core.models.category import Category
from core.models.event import Event
from core.models.candidate import Candidate
from core.models.common import TimeStampedModel

class VoteTransaction(TimeStampedModel):
    PAYMENT_METHOD_CHOICES = [('momo', 'Mobile Money'), ('card', 'Card'), ('bank', 'Bank')]
    PROVIDER_CHOICES = [('mtn', 'MTN'), ('airtel', 'Airtel'), ('telecel', 'Telecel')]
    PAYMENT_STATUS_CHOICES = [('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    payment_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS_CHOICES)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Tx: {self.payment_reference} - {self.vote_count} votes"
