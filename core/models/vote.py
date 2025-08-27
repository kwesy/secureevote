import uuid
from django.db import models
from core.models.candidate import Candidate
from core.models.common import TimeStampedModel
from payments.models.transaction import Transaction

class VoteTransaction(TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField()
    payment = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Tx: {self.candidate.name} - {self.vote_count} votes"
