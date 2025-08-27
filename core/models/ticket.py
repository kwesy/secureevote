import uuid
from django.db import models
from core.models.event import Event
from core.models.common import TimeStampedModel
from payments.models.transaction import Transaction

class Ticket(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    sold = models.PositiveIntegerField(default=0)
    desc = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Ticket: {self.id[:5]} - {self.type} votes"

class TicketSale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    payment = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    recipient_contact = models.CharField(max_length=15)
    recipient_email = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Ticket Sale: {self.payment_reference} - {self.amount} amount"