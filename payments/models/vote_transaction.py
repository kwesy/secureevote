from django.db import models
from core.models.event import Event
from core.models.candidate import Candidate
from core.models.common import TimeStampedModel

class VoteTransaction(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Tx: {self.payment_reference} - {self.vote_count} votes"
