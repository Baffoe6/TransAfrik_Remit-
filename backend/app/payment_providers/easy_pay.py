import logging
from typing import Any

from app.payment_providers.base import (
    PaymentProvider,
    PaymentReferenceRequest,
    PaymentReferenceResult,
    PaymentStatusResult,
    WebhookResult,
)
from app.payment_providers.voucher import (
    default_expiry,
    generate_barcode_data,
    generate_qr_url,
    generate_reference_number,
    generate_voucher_number,
)

logger = logging.getLogger(__name__)


class EasyPayProvider(PaymentProvider):
    """
    EasyPay voucher payment collection provider.

    Architecture mirrors Pay@: voucher → outlet payment → webhook settlement.
    """

    VOUCHER_EXPIRY_DAYS = 3
    PROVIDER = "easy_pay"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.api_base_url = self.config.get("api_base_url")
        self.client_id = self.config.get("client_id")
        self.is_live = bool(self.api_base_url and self.client_id)

    @property
    def provider_code(self) -> str:
        return self.PROVIDER

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        if self.is_live:
            return self._generate_live_reference(request)
        return self._generate_stub_reference(request)

    def _generate_stub_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        ref = generate_reference_number(self.PROVIDER, request.transfer_reference)
        voucher = generate_voucher_number("EPV")
        expiry = default_expiry(self.VOUCHER_EXPIRY_DAYS)
        barcode = generate_barcode_data(self.PROVIDER, ref, voucher, request.amount)
        qr = generate_qr_url(self.PROVIDER, ref)

        return PaymentReferenceResult(
            success=True,
            reference_number=ref,
            voucher_number=voucher,
            barcode_data=barcode,
            qr_data=qr,
            expiry_date=expiry,
            message="Pay cash at any EasyPay partner outlet",
            metadata={
                "mode": "sandbox",
                "provider": self.PROVIDER,
                "amount_zar": str(request.amount),
            },
        )

    def _generate_live_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        logger.info("EasyPay live API not yet connected — using sandbox voucher for %s", request.transfer_reference)
        result = self._generate_stub_reference(request)
        result.metadata = {**(result.metadata or {}), "mode": "api_fallback"}
        return result

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        return PaymentStatusResult(reference_number=reference_number, status="awaiting_payment")

    def process_webhook(self, payload: dict) -> WebhookResult:
        event = payload.get("event_type") or payload.get("type") or payload.get("status")
        ref = payload.get("reference") or payload.get("reference_number") or payload.get("bill_number")

        if event in ("payment.received", "payment_received", "paid", "SETTLED") and ref:
            return WebhookResult(
                success=True,
                reference_number=str(ref),
                status="paid",
                raw_payload=payload,
            )
        if event in ("payment.expired", "expired", "CANCELLED") and ref:
            return WebhookResult(success=True, reference_number=str(ref), status="expired", raw_payload=payload)

        return WebhookResult(success=False, raw_payload=payload)

    def validate_credentials(self) -> bool:
        return self.is_live

    def get_api_status(self) -> dict[str, Any]:
        return {
            "provider": self.PROVIDER,
            "mode": "live" if self.is_live else "sandbox",
            "api_base_url": self.api_base_url,
            "client_configured": bool(self.client_id),
        }
