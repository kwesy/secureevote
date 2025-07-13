from django.db import models

class WebhookLog(models.Model):
    event_id = models.CharField(max_length=100)
    candidate_id = models.CharField(max_length=100)
    payload = models.JSONField()
    is_valid = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WebhookLog {self.id} ({'valid' if self.is_valid else 'invalid'})"
