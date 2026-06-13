import logging
from decimal import Decimal

from app.fx_sources.base import FxFeedProvider, FxFeedRate

logger = logging.getLogger(__name__)


class ExchangeRateApiProvider(FxFeedProvider):
    """ExchangeRate-API feed (placeholder — uses configured fallback rate when no API key)."""

    def __init__(self, api_key: str | None = None, fallback_rate: str = "0.72"):
        self.api_key = api_key
        self.fallback_rate = Decimal(fallback_rate)

    @property
    def provider_code(self) -> str:
        return "exchange_rate_api"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def fetch_rate(self, from_currency: str, to_currency: str) -> FxFeedRate | None:
        if not self.api_key:
            logger.info("ExchangeRateAPI: no API key — using fallback rate")
            return FxFeedRate(from_currency, to_currency, self.fallback_rate, self.provider_code)
        # TODO: HTTP GET https://v6.exchangerate-api.com/v6/{key}/pair/{from}/{to}
        return FxFeedRate(from_currency, to_currency, self.fallback_rate, self.provider_code)
