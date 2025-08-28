from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
import secrets

def generate_secure_otp(length=6):
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def generate_prefix():
    return ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for _ in range(4))

class OTP(models.Model):
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=6, default=generate_secure_otp, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    prefix = models.CharField(max_length=6, default=generate_prefix)

    def is_expired(self):
        return timezone.now() > self.updated_at + timedelta(minutes=5)  # 5 min expiry
    
    def verify(self, code):
        """
        Verify the OTP code.
        :param code: The OTP code to verify.
        :return: True if the code is correct and not expired, False otherwise.
        """

        if self.is_expired() or self.is_verified: # OTP is expired or already verified
            return False

        if self.code == code:
            self.is_verified = True
            self.save()
            return True
        return False
    

    def __str__(self):
        return f"OTP for {self.request_id} - {self.code}"