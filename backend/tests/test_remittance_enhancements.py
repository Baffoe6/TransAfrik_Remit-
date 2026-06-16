"""Corridor FX and beneficiary auto-approval tests."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.beneficiary_compliance import resolve_beneficiary_status
from app.models.enums import BeneficiaryStatus


def test_resolve_beneficiary_status_approved_when_no_flags():
    assert resolve_beneficiary_status([]) == BeneficiaryStatus.APPROVED


def test_resolve_beneficiary_status_approved_even_when_flagged():
    flags = [{"type": "name_mismatch", "message": "test"}]
    assert resolve_beneficiary_status(flags) == BeneficiaryStatus.APPROVED


def test_pricing_uses_destination_currency(monkeypatch):
    from app.services import pricing

    captured = {}

    def fake_rate(db, *, from_currency, to_currency, on_date=None):
        captured["pair"] = (from_currency, to_currency)
        return Decimal("7.15"), {"base_rate": "7.00", "source": "manual"}

    def fake_fee(db, amount, **kwargs):
        return Decimal("49"), None

    monkeypatch.setattr(pricing, "get_effective_fx_rate", fake_rate)
    monkeypatch.setattr(pricing, "calculate_fee", fake_fee)
    monkeypatch.setattr(
        pricing,
        "resolve_corridor_currencies",
        lambda db, destination_country, source_country="ZA": ("ZAR", "KES", "ZA-KE"),
    )

    result = pricing.calculate_transfer_amounts(MagicMock(), Decimal("1000"), destination_country="KE")
    assert captured["pair"] == ("ZAR", "KES")
    assert result["to_currency"] == "KES"
    assert result["corridor_code"] == "ZA-KE"
