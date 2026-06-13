from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.payment_providers.base import PaymentReferenceRequest, PaymentReferenceResult, PaymentStatusResult, WebhookResult


@dataclass
class RetailNetworkInfo:
    code: str
    name: str
    network_type: str
    supported_channels: list[str]


class RetailPaymentNetwork(ABC):
    """Unified abstraction for South African retail payment networks."""

    @property
    @abstractmethod
    def network_code(self) -> str:
        pass

    @abstractmethod
    def get_network_info(self) -> RetailNetworkInfo:
        pass

    @abstractmethod
    def generate_voucher(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        pass

    @abstractmethod
    def check_status(self, reference_number: str) -> PaymentStatusResult:
        pass

    @abstractmethod
    def process_webhook(self, payload: dict[str, Any]) -> WebhookResult:
        pass
