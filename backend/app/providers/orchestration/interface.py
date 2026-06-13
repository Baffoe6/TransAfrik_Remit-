from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class OrchestrationQuoteRequest:
    source_country: str
    destination_country: str
    send_amount: Decimal
    send_currency: str = "ZAR"
    receive_currency: str | None = None
    beneficiary_type: str = "mobile_money"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationQuote:
    provider_code: str
    send_amount: Decimal
    receive_amount: Decimal
    exchange_rate: Decimal
    fee_amount: Decimal
    send_currency: str
    receive_currency: str
    estimated_delivery: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationTransferRequest:
    transfer_id: int
    reference: str
    source_country: str
    destination_country: str
    send_amount: Decimal
    receive_amount: Decimal
    exchange_rate: Decimal
    fee_amount: Decimal
    send_currency: str
    receive_currency: str
    sender_name: str
    beneficiary_name: str
    beneficiary_details: dict[str, Any]
    payment_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationTransferResult:
    success: bool
    provider_reference: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationStatusResult:
    reference: str
    status: str
    provider_reference: str | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationReconcileResult:
    success: bool
    matched: int = 0
    unmatched: int = 0
    details: list[dict[str, Any]] = field(default_factory=list)


class OrchestrationProvider(ABC):
    """Unified provider interface for multi-provider orchestration."""

    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def quote(self, request: OrchestrationQuoteRequest) -> OrchestrationQuote:
        pass

    @abstractmethod
    def create_transfer(self, request: OrchestrationTransferRequest) -> OrchestrationTransferResult:
        pass

    @abstractmethod
    def get_status(self, reference: str) -> OrchestrationStatusResult:
        pass

    @abstractmethod
    def cancel_transfer(self, reference: str) -> OrchestrationTransferResult:
        pass

    @abstractmethod
    def reconcile(self, reference: str, provider_data: dict[str, Any]) -> OrchestrationReconcileResult:
        pass

    def is_available(self) -> bool:
        return True
