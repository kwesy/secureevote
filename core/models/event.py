import shortuuid
from django.db import models
from .user import User
from .common import TimeStampedModel

def generate_shortcode():
    return shortuuid.ShortUUID().random(length=8)

class Event(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    shortcode = models.CharField(max_length=10, unique=True, default=generate_shortcode)
    amount_per_vote = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.shortcode})"
