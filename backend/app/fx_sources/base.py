from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FxFeedRate:
    from_currency: str
    to_currency: str
    rate: Decimal
    source: str


class FxFeedProvider(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def fetch_rate(self, from_currency: str, to_currency: str) -> FxFeedRate | None:
        pass

    def is_configured(self) -> bool:
        return True
