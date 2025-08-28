import uuid
from django.db import models
from core.models.category import Category
from core.models.event import Event
from core.models.candidate import Candidate
from core.models.common import TimeStampedModel
from payments.models.transaction import Transaction

class WithdrawalTransaction(TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='withdrawals')
    otp = models.ForeignKey('core.OTP', on_delete=models.CASCADE, related_name='withdrawals')
    is_verified = models.BooleanField(default=False)
