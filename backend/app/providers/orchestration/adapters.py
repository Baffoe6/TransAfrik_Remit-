"""Adapters mapping existing remittance/payment providers to OrchestrationProvider."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.payment_providers.base import PaymentReferenceRequest
from app.payment_providers.registry import get_payment_provider
from app.providers.base import TransferRequest as RemittanceTransferRequest
from app.providers.orchestration.interface import (
    OrchestrationProvider,
    OrchestrationQuote,
    OrchestrationQuoteRequest,
    OrchestrationReconcileResult,
    OrchestrationStatusResult,
    OrchestrationTransferRequest,
    OrchestrationTransferResult,
)
from app.providers.registry import get_provider as get_remittance_provider


class _RemittanceOrchestrationAdapter(OrchestrationProvider):
    def __init__(self, provider_class: str):
        self._provider_class = provider_class
        self._provider = get_remittance_provider(provider_class)

    @property
    def provider_code(self) -> str:
        return self._provider.provider_code

    def quote(self, request: OrchestrationQuoteRequest) -> OrchestrationQuote:
        rate = Decimal(request.metadata.get("exchange_rate", "0.72"))
        fee = Decimal(request.metadata.get("fee_amount", "49"))
        receive = (request.send_amount * rate).quantize(Decimal("0.01"))
        return OrchestrationQuote(
            provider_code=self.provider_code,
            send_amount=request.send_amount,
            receive_amount=receive,
            exchange_rate=rate,
            fee_amount=fee,
            send_currency=request.send_currency,
            receive_currency=request.receive_currency or "GHS",
            metadata={"adapter": "remittance", "provider_class": self._provider_class},
        )

    def create_transfer(self, request: OrchestrationTransferRequest) -> OrchestrationTransferResult:
        remittance_req = RemittanceTransferRequest(
            transfer_id=request.transfer_id,
            reference=request.reference,
            sender_name=request.sender_name,
            sender_phone=request.beneficiary_details.get("sender_phone"),
            sender_id_number=request.beneficiary_details.get("sender_id_number"),
            beneficiary_name=request.beneficiary_name,
            beneficiary_country=request.destination_country,
            mobile_money_provider=request.beneficiary_details.get("mobile_money_provider", ""),
            mobile_wallet_number=request.beneficiary_details.get("mobile_wallet_number", ""),
            send_amount_zar=request.send_amount,
            receive_amount_ghs=request.receive_amount,
            exchange_rate=request.exchange_rate,
            fee_zar=request.fee_amount,
            payment_reference=request.payment_reference,
        )
        result = self._provider.create_transfer(remittance_req)
        return OrchestrationTransferResult(
            success=result.success,
            provider_reference=result.provider_reference,
            message=result.message,
            metadata=result.metadata or {},
        )

    def get_status(self, reference: str) -> OrchestrationStatusResult:
        result = self._provider.get_transfer_status(reference)
        return OrchestrationStatusResult(
            reference=result.reference,
            status=result.status,
            provider_reference=result.provider_reference,
            updated_at=result.updated_at,
            metadata=result.metadata or {},
        )

    def cancel_transfer(self, reference: str) -> OrchestrationTransferResult:
        result = self._provider.cancel_transfer(reference)
        return OrchestrationTransferResult(
            success=result.success,
            provider_reference=result.provider_reference,
            message=result.message,
            metadata=result.metadata or {},
        )

    def reconcile(self, reference: str, provider_data: dict[str, Any]) -> OrchestrationReconcileResult:
        result = self._provider.reconcile_transfer(reference, provider_data)
        return OrchestrationReconcileResult(
            success=result.success,
            matched=result.matched,
            unmatched=result.unmatched,
            details=result.details,
        )


class _PaymentOrchestrationAdapter(OrchestrationProvider):
    """Adapter for collection networks used in hybrid orchestration flows."""

    def __init__(self, provider_class: str, config: dict | None = None):
        self._provider_class = provider_class
        self._provider = get_payment_provider(provider_class, config)

    @property
    def provider_code(self) -> str:
        return self._provider.provider_code

    def quote(self, request: OrchestrationQuoteRequest) -> OrchestrationQuote:
        fee = Decimal(request.metadata.get("fee_amount", "15"))
        return OrchestrationQuote(
            provider_code=self.provider_code,
            send_amount=request.send_amount,
            receive_amount=request.send_amount - fee,
            exchange_rate=Decimal("1"),
            fee_amount=fee,
            send_currency=request.send_currency,
            receive_currency=request.send_currency,
            metadata={"adapter": "payment_collection"},
        )

    def create_transfer(self, request: OrchestrationTransferRequest) -> OrchestrationTransferResult:
        ref_req = PaymentReferenceRequest(
            transfer_reference=request.reference,
            amount=request.send_amount,
            currency=request.send_currency,
            customer_email=request.beneficiary_details.get("customer_email", "customer@transafrik.co.za"),
            customer_name=request.sender_name,
            customer_phone=request.beneficiary_details.get("sender_phone"),
        )
        result = self._provider.generate_reference(ref_req)
        return OrchestrationTransferResult(
            success=result.success,
            provider_reference=result.reference_number,
            message="Payment reference generated",
            metadata={
                "voucher_number": result.voucher_number,
                "barcode_data": result.barcode_data,
            },
        )

    def get_status(self, reference: str) -> OrchestrationStatusResult:
        result = self._provider.check_payment_status(reference)
        return OrchestrationStatusResult(
            reference=reference,
            status=result.status,
            updated_at=datetime.now(UTC),
            metadata={"paid_at": result.paid_at},
        )

    def cancel_transfer(self, reference: str) -> OrchestrationTransferResult:
        return OrchestrationTransferResult(success=False, message="Payment references cannot be cancelled via API")

    def reconcile(self, reference: str, provider_data: dict[str, Any]) -> OrchestrationReconcileResult:
        status = self.get_status(reference)
        matched = 1 if status.status in ("paid", "verified", "completed") else 0
        return OrchestrationReconcileResult(
            success=matched == 1,
            matched=matched,
            unmatched=1 - matched,
            details=[{"reference": reference, "status": status.status}],
        )


def create_orchestration_provider(provider_code: str, config: dict | None = None) -> OrchestrationProvider:
    payment_codes = {"pay_at", "easy_pay"}
    if provider_code in payment_codes:
        return _PaymentOrchestrationAdapter(provider_code, config)
    return _RemittanceOrchestrationAdapter(provider_code)
