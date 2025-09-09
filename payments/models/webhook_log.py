from django.db import models
from core.models.common import TimeStampedModel

class WebhookLog(TimeStampedModel):
    event = models.CharField(max_length=100)
    product = models.IntegerField() # Vote -> 0, Ticket -> 1
    instance_id = models.CharField(max_length=100)
    payload = models.JSONField()
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f"WebhookLog {self.id} ({'valid' if self.is_valid else 'invalid'})"
