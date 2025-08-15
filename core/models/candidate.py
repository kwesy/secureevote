from django.db import models
from .event import Event
from .category import Category 
from .common import TimeStampedModel

class Candidate(TimeStampedModel):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='candidates')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='candidates/photos/', blank=True, null=True)
    description = models.TextField(blank=True)
    extra_info = models.TextField(blank=True)
    achivements = models.JSONField(blank=True, default=list)
    vote_count = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("event", "name", "category")

    def __str__(self):
        return f"{self.name} ({self.event.shortcode})"
