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

    def fake_fee_included(db, amount_to_pay, **kwargs):
        from app.services.fee_engine import FeeIncludedResult

        return FeeIncludedResult(Decimal("49"), amount_to_pay - Decimal("49"))

    monkeypatch.setattr(pricing, "get_effective_fx_rate", fake_rate)
    monkeypatch.setattr(pricing, "calculate_fee_included", fake_fee_included)
    monkeypatch.setattr(
        pricing,
        "resolve_corridor_currencies",
        lambda db, destination_country, source_country="ZA": ("ZAR", "KES", "ZA-KE"),
    )

    result = pricing.calculate_transfer_amounts(MagicMock(), Decimal("1000"), destination_country="KE")
    assert captured["pair"] == ("ZAR", "KES")
    assert result["to_currency"] == "KES"
    assert result["corridor_code"] == "ZA-KE"
    assert result["amount_to_pay_zar"] == Decimal("1000")
    assert result["send_amount_zar"] == Decimal("951")
    assert result["fee_zar"] == Decimal("49")
    assert result["total_amount_zar"] == Decimal("1000")
    assert result["receive_amount"] == (Decimal("951") * Decimal("7.15")).quantize(Decimal("0.01"))
    assert result["delivery_method"]
    assert result["estimated_delivery"]


def test_build_customer_quote_strips_internal_fields():
    from app.services.pricing import build_customer_quote

    amounts = {
        "amount_to_pay_zar": Decimal("1000"),
        "fee_zar": Decimal("25"),
        "exchange_rate": Decimal("0.615"),
        "customer_rate": Decimal("0.615"),
        "receive_amount": Decimal("600"),
        "receive_amount_ghs": Decimal("600"),
        "total_amount_zar": Decimal("1000"),
        "from_currency": "ZAR",
        "to_currency": "GHS",
        "corridor_code": "ZA-GH",
        "delivery_method": "Mobile Money",
        "estimated_delivery": "Same day",
        "base_rate": Decimal("0.62"),
        "markup_percentage": Decimal("1.5"),
        "provider": "manual",
    }
    quote = build_customer_quote(amounts)
    assert "base_rate" not in quote
    assert "markup_percentage" not in quote
    assert "provider" not in quote
    assert quote["amount_to_pay_zar"] == Decimal("1000")
    assert quote["delivery_method"] == "Mobile Money"


def test_calculate_fee_included_flat():
    from decimal import Decimal
    from unittest.mock import MagicMock

    from app.models.fee_rule import FeeRule
    from app.services.fee_engine import calculate_fee_included

    rule = FeeRule(fee_type="flat", fee_value=Decimal("25"), min_amount_zar=Decimal("0"))
    db = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = []

    def fake_calc(db, amount, **kwargs):
        return Decimal("25"), rule

    import app.services.fee_engine as fee_engine

    orig = fee_engine.calculate_fee
    fee_engine.calculate_fee = fake_calc
    try:
        result = calculate_fee_included(db, Decimal("1000"))
        assert result.fee_zar == Decimal("25")
        assert result.net_send_zar == Decimal("975")
    finally:
        fee_engine.calculate_fee = orig
