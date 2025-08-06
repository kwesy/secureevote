from django.db import models
from .user import User
from .common import TimeStampedModel


class Category(TimeStampedModel):
    event = models.ForeignKey("core.Event", on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("event", "name")

    def __str__(self):
        return f"{self.name} ({self.event.shortcode})"
