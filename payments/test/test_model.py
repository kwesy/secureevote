import pytest
from django.db import IntegrityError
from payments.models import Transaction
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestTransactionModel:
    def test_transaction_creation_defaults(self):
        tx = Transaction.objects.create(
            amount=50.00,
            channel="momo",
            provider="mtn",
            phone_number="233555123456",
            type="payment",
        )
        assert tx.amount == 50.00
        assert tx.channel == "momo"
        assert tx.provider == "mtn"
        assert tx.phone_number == "233555123456"
        assert tx.currency == "GHS"       # default currency
        assert tx.status == "pending"     # default status
        assert tx.type == "payment"
        assert tx.external_payment_id is None
        assert tx.desc is None
        assert tx.gateway is None

    def test_transaction_str_representation(self):
        tx = Transaction.objects.create(
            amount=100.00,
            channel="momo",
            provider="airtel",
            phone_number="233575987654",
            type="deposit"
        )
        tx_str = str(tx)
        assert str(tx.id)[:5] in tx_str
        assert "100.0" in tx_str
        assert "momo" in tx_str

    def test_unique_external_payment_id(self):
        Transaction.objects.create(
            amount=20.00,
            channel="momo",
            provider="mtn",
            phone_number="233555000111",
            type="withdrawal",
            external_payment_id="ext123"
        )
        with pytest.raises(IntegrityError):
            Transaction.objects.create(
                amount=30.00,
                channel="momo",
                provider="mtn",
                phone_number="233555000222",
                type="withdrawal",
                external_payment_id="ext123"  # duplicate
            )

    def test_invalid_channel_choice(self):
        with pytest.raises(ValidationError):
            Transaction.objects.create(
                amount=15.00,
                channel="crypto",  # invalid
                provider="mtn",
                phone_number="233555999999",
                type="payment"
            ).full_clean()

    def test_invalid_provider_choice(self):
        with pytest.raises(ValidationError):
            Transaction.objects.create(
                amount=25.00,
                channel="momo",
                provider="vodafone",  # invalid
                phone_number="233555333444",
                type="payment"
            ).full_clean()

    def test_invalid_status_choice(self):
        tx = Transaction(
            amount=40.00,
            channel="bank",
            provider="telecel",
            phone_number="233555121212",
            type="transfer",
            status="unknown"  # invalid
        )
        with pytest.raises(ValidationError):
            tx.full_clean()

    def test_invalid_type_choice(self):
        tx = Transaction(
            amount=60.00,
            channel="card",
            provider="mtn",
            phone_number="233555555555",
            type="loan"  # invalid
        )
        with pytest.raises(ValidationError):
            tx.full_clean()
