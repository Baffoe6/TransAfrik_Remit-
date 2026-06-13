from app.fx_sources.base import FxFeedProvider
from app.fx_sources.currencylayer import CurrencyLayerProvider
from app.fx_sources.exchange_rate_api import ExchangeRateApiProvider
from app.fx_sources.openexchangerates import OpenExchangeRatesProvider

_FEED_PROVIDERS: dict[str, type] = {
    "exchange_rate_api": ExchangeRateApiProvider,
    "currencylayer": CurrencyLayerProvider,
    "openexchangerates": OpenExchangeRatesProvider,
}


def get_fx_feed_provider(code: str, config: dict | None = None) -> FxFeedProvider:
    factory = _FEED_PROVIDERS.get(code)
    if not factory:
        raise ValueError(f"Unknown FX feed provider: {code}")
    config = config or {}
    return factory(
        api_key=config.get("api_key"),
        fallback_rate=str(config.get("fallback_rate", "0.72")),
    )


def list_fx_feed_providers() -> list[str]:
    return list(_FEED_PROVIDERS.keys())
