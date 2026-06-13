from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class TransferRequest:
    transfer_id: int
    reference: str
    sender_name: str
    sender_phone: str | None
    sender_id_number: str | None
    beneficiary_name: str
    beneficiary_country: str
    mobile_money_provider: str
    mobile_wallet_number: str
    send_amount_zar: Decimal
    receive_amount_ghs: Decimal
    exchange_rate: Decimal
    fee_zar: Decimal
    payment_reference: str | None = None
    status: str = "ready_for_processing"


@dataclass
class ProviderTransferResult:
    success: bool
    provider_reference: str | None = None
    message: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ProviderStatusResult:
    reference: str
    status: str
    provider_reference: str | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class BatchExportResult:
    success: bool
    batch_id: str
    file_path: str
    file_format: str
    transfer_count: int
    message: str | None = None
    excel_path: str | None = None


@dataclass
class ReconcileResult:
    success: bool
    matched: int
    unmatched: int
    details: list[dict[str, Any]] = field(default_factory=list)


class RemittanceProvider(ABC):
    """Abstract base for outbound remittance provider integrations."""

    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def create_transfer(self, request: TransferRequest) -> ProviderTransferResult:
        pass

    @abstractmethod
    def get_transfer_status(self, reference: str) -> ProviderStatusResult:
        pass

    @abstractmethod
    def cancel_transfer(self, reference: str) -> ProviderTransferResult:
        pass

    @abstractmethod
    def export_batch(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        pass

    @abstractmethod
    def reconcile_transfer(self, reference: str, provider_data: dict[str, Any]) -> ReconcileResult:
        pass

    def generate_batch(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        return self.export_batch(transfers, output_dir)

    def export_csv(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        return self.export_batch(transfers, output_dir)

    def export_excel(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        raise NotImplementedError

    def reconcile_transactions(self, references: list[str], provider_data: list[dict[str, Any]]) -> ReconcileResult:
        details = []
        matched = 0
        for ref, data in zip(references, provider_data):
            result = self.reconcile_transfer(ref, data)
            if result.matched:
                matched += 1
            details.extend(result.details)
        return ReconcileResult(
            success=matched == len(references),
            matched=matched,
            unmatched=len(references) - matched,
            details=details,
        )

    def mark_as_submitted(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(success=True, message=f"{reference} marked as submitted")

    def mark_as_completed(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(success=True, message=f"{reference} marked as completed")
