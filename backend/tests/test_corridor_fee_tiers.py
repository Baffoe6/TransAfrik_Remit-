"""Corridor fee tier selection tests."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.models.corridor_fee import CorridorFeeRule, CorridorFeeTier
from app.services.fee_engine import calculate_fee_included, resolve_corridor_fee_tier


def _gh_rule_with_tiers() -> CorridorFeeRule:
    rule = CorridorFeeRule(
        id=1,
        corridor_code="ZA-GH",
        source_country="ZA",
        destination_country="GH",
        name="South Africa → Ghana",
        provider_cost_pct=Decimal("1.5"),
        is_active=True,
        priority=100,
    )
    tiers = [
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("0"), max_amount_zar=Decimal("500"), fee_zar=Decimal("20"), sort_order=0, is_active=True),
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("501"), max_amount_zar=Decimal("1000"), fee_zar=Decimal("30"), sort_order=1, is_active=True),
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("1001"), max_amount_zar=Decimal("2500"), fee_zar=Decimal("45"), sort_order=2, is_active=True),
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("2501"), max_amount_zar=Decimal("5000"), fee_zar=Decimal("70"), sort_order=3, is_active=True),
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("5001"), max_amount_zar=Decimal("10000"), fee_zar=Decimal("100"), sort_order=4, is_active=True),
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("10001"), max_amount_zar=Decimal("20000"), fee_zar=Decimal("150"), sort_order=5, is_active=True),
        CorridorFeeTier(rule_id=1, min_amount_zar=Decimal("20001"), max_amount_zar=Decimal("50000"), fee_zar=Decimal("250"), sort_order=6, is_active=True),
    ]
    rule.tiers = tiers
    return rule


@pytest.mark.parametrize(
    "amount,expected_fee",
    [
        (Decimal("500"), Decimal("20")),
        (Decimal("501"), Decimal("30")),
        (Decimal("1000"), Decimal("30")),
        (Decimal("1001"), Decimal("45")),
        (Decimal("2500"), Decimal("45")),
        (Decimal("2501"), Decimal("70")),
        (Decimal("5000"), Decimal("70")),
        (Decimal("5001"), Decimal("100")),
        (Decimal("10000"), Decimal("100")),
        (Decimal("10001"), Decimal("150")),
        (Decimal("20000"), Decimal("150")),
        (Decimal("20001"), Decimal("250")),
        (Decimal("50000"), Decimal("250")),
    ],
)
def test_za_gh_tier_fees(amount, expected_fee):
    rule = _gh_rule_with_tiers()
    db = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [rule]

    match = resolve_corridor_fee_tier(db, amount, destination_country="GH")
    assert match is not None
    fee, tier, matched_rule = match
    assert fee == expected_fee
    assert matched_rule.corridor_code == "ZA-GH"


def test_fee_included_uses_corridor_tier():
    rule = _gh_rule_with_tiers()
    db = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [rule]

    result = calculate_fee_included(db, Decimal("1000"), destination_country="GH")
    assert result.fee_zar == Decimal("30")
    assert result.net_send_zar == Decimal("970")
    assert result.corridor_tier is not None
    assert result.corridor_tier.fee_zar == Decimal("30")


def test_pricing_profitability_fields(monkeypatch):
    from app.services import pricing
    from app.services.fee_engine import FeeIncludedResult

    tier = CorridorFeeTier(
        id=2,
        rule_id=1,
        min_amount_zar=Decimal("501"),
        max_amount_zar=Decimal("1000"),
        fee_zar=Decimal("30"),
        sort_order=1,
        is_active=True,
    )

    monkeypatch.setattr(
        pricing,
        "get_effective_fx_rate",
        lambda *a, **k: (Decimal("0.615"), {"base_rate": "0.62", "source": "manual"}),
    )
    monkeypatch.setattr(
        pricing,
        "calculate_fee_included",
        lambda db, amount, **kwargs: FeeIncludedResult(
            Decimal("30"),
            Decimal("970"),
            corridor_tier=tier,
            corridor_rule=_gh_rule_with_tiers(),
        ),
    )
    monkeypatch.setattr(
        pricing,
        "resolve_corridor_currencies",
        lambda db, destination_country, source_country="ZA": ("ZAR", "GHS", "ZA-GH"),
    )

    result = pricing.calculate_transfer_amounts(MagicMock(), Decimal("1000"), destination_country="GH")
    assert result["fee_zar"] == Decimal("30")
    assert result["send_amount_zar"] == Decimal("970")
    assert result["provider_cost_zar"] is not None
    assert result["fx_margin_zar"] is not None
    assert result["net_revenue_zar"] is not None
    assert result["corridor_fee_tier_id"] == 2
