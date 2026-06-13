"""Provider orchestration router tests."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.providers.orchestration.interface import OrchestrationQuoteRequest
from app.services import provider_router


def test_list_available_providers():
    providers = provider_router.list_available_providers()
    assert "mock_mukuru" in providers
    assert "flutterwave" in providers
    assert "pay_at" in providers


def test_get_orchestration_provider_mock_mukuru():
    provider = provider_router.get_orchestration_provider(MagicMock(), "mock_mukuru")
    assert provider.provider_code == "mock_mukuru"


def test_get_orchestration_provider_unknown():
    with pytest.raises(ValueError, match="Unsupported"):
        provider_router.get_orchestration_provider(MagicMock(), "unknown_provider")


def test_quote_transfer_without_corridor(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    quote = provider_router.quote_transfer(
        db,
        OrchestrationQuoteRequest(
            source_country="ZA",
            destination_country="XX",
            send_amount=Decimal("1000"),
        ),
        user_id=None,
    )
    assert quote.send_amount == Decimal("1000")
    assert quote.provider_code == "mock_mukuru"
