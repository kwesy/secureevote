from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    metadata = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"
