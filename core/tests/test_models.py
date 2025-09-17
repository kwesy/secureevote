from core.models.common import TimeStampedModel
import pytest
from django.utils import timezone
from core.models import User, Event, Category, Candidate, OTP
from django.core.exceptions import ValidationError
from django.db import IntegrityError
# from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
import time


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_success(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            organization_name="Event Corp"
        )
        assert user.email == "test@example.com"
        assert user.check_password("strongpassword123")
        assert user.organization_name == "Event Corp"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.balance == 0
        assert user.transfer_allowed is True
        assert user.transfer_limit == 1000

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match="Users must have an email address"):
            User.objects.create_user(
                email="",
                password="password123",
                organization_name="Event Corp"
            )

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="supersecret",
            organization_name="Admin Corp"
        )
        assert superuser.is_superuser is True
        assert superuser.is_staff is True
        assert superuser.is_active is True

    def test_create_superuser_invalid_staff_flag(self):
        with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
            User.objects.create_superuser(
                email="admin2@example.com",
                password="supersecret",
                organization_name="Admin Corp",
                is_staff=False
            )

    def test_create_superuser_invalid_superuser_flag(self):
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
            User.objects.create_superuser(
                email="admin3@example.com",
                password="supersecret",
                organization_name="Admin Corp",
                is_superuser=False
            )

    def test_str_returns_email(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="testpass",
            organization_name="Org"
        )
        assert str(user) == "user@example.com"

    def test_user_with_otp_relation(self, django_user_model):
        otp = OTP.objects.create()
        user = django_user_model.objects.create_user(
            email="otpuser@example.com",
            password="password123",
            organization_name="OTP Org",
            otp=otp
        )
        assert user.otp == otp


@pytest.mark.django_db
class TestOTPModel:
    def test_otp_creation_defaults(self):
        otp = OTP.objects.create()
        assert otp.code is not None
        assert len(otp.code) == 6
        assert otp.prefix is not None
        assert len(otp.prefix) <= 6
        assert otp.is_verified is False
        assert otp.request_id is not None

    def test_str_representation(self):
        otp = OTP.objects.create()
        otp_str = str(otp)
        assert str(otp.request_id) in otp_str
        assert otp.code in otp_str

    def test_is_expired_false(self):
        otp = OTP.objects.create()
        assert otp.is_expired() is False

    def test_is_expired_true(self):
        otp = OTP.objects.create()
        otp.updated_at = timezone.now() - timedelta(minutes=10)
        # otp.save() #otherwise auto_now resets the time
        assert otp.is_expired() is True

    def test_verify_success(self):
        otp = OTP.objects.create(code="123456")
        assert otp.verify("123456") is True
        otp.refresh_from_db()
        assert otp.is_verified is True

    def test_verify_wrong_code(self):
        otp = OTP.objects.create(code="123456")
        assert otp.verify("654321") is False
        otp.refresh_from_db()
        assert otp.is_verified is False

    def test_verify_expired_code(self):
        otp = OTP.objects.create(code="123456")
        otp.updated_at = timezone.now() - timedelta(minutes=10)
        # otp.save() otherwise auto_now resets the time
        assert otp.verify("123456") is False

    def test_verify_already_verified(self):
        otp = OTP.objects.create(code="123456", is_verified=True)
        assert otp.verify("123456") is False
