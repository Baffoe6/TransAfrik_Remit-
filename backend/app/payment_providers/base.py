from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass
class PaymentReferenceRequest:
    transfer_reference: str
    amount: Decimal
    currency: str
    customer_name: str
    customer_email: str
    customer_phone: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class PaymentReferenceResult:
    success: bool
    reference_number: str
    voucher_number: str | None = None
    barcode_data: str | None = None
    qr_data: str | None = None
    expiry_date: date | None = None
    banking_instructions: dict[str, Any] | None = None
    message: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class PaymentStatusResult:
    reference_number: str
    status: str
    paid_at: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class WebhookResult:
    success: bool
    reference_number: str | None = None
    status: str | None = None
    raw_payload: dict[str, Any] | None = None


class PaymentProvider(ABC):
    """Abstract base for inbound payment collection integrations."""

    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        pass

    @abstractmethod
    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        pass

    @abstractmethod
    def process_webhook(self, payload: dict[str, Any]) -> WebhookResult:
        pass

    def initiate_payment(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        """Optional: for instant EFT/card flows that redirect to a gateway."""
        return self.generate_reference(request)
