"""FX feed engine tests."""

from decimal import Decimal

from app.fx_sources.exchange_rate_api import ExchangeRateApiProvider
from app.fx_sources.registry import get_fx_feed_provider, list_fx_feed_providers


def test_list_fx_feed_providers():
    providers = list_fx_feed_providers()
    assert "exchange_rate_api" in providers
    assert "currencylayer" in providers
    assert "openexchangerates" in providers


def test_exchange_rate_api_fallback():
    provider = get_fx_feed_provider("exchange_rate_api", {"fallback_rate": "0.75"})
    rate = provider.fetch_rate("ZAR", "GHS")
    assert rate is not None
    assert rate.rate == Decimal("0.75")
    assert rate.source == "exchange_rate_api"


def test_currencylayer_without_key():
    provider = ExchangeRateApiProvider(api_key=None, fallback_rate="0.70")
    assert provider.is_configured() is False
    rate = provider.fetch_rate("ZAR", "GHS")
    assert rate.rate == Decimal("0.70")
