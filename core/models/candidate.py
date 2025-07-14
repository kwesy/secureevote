from django.db import models
from .event import Event
from .common import TimeStampedModel

class Candidate(TimeStampedModel):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='candidates/photos/', blank=True, null=True)
    description = models.TextField(blank=True)
    vote_count = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.event.shortcode})"
