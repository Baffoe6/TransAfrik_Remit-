from abc import abstractmethod
from typing import Any

from app.providers.base import RemittanceProvider


class MukuruProvider(RemittanceProvider):
    """Mukuru connector interface — all Mukuru implementations must extend this."""

    @abstractmethod
    def validate_credentials(self) -> bool:
        pass

    @abstractmethod
    def get_api_status(self) -> dict[str, Any]:
        pass

    @property
    def provider_family(self) -> str:
        return "mukuru"
