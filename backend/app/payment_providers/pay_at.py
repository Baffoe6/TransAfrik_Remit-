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


class PayAtProvider(PaymentProvider):
    """
    Pay@ voucher payment collection provider.

    Architecture: voucher generation → retailer settlement → webhook confirmation.
    Live API calls are gated behind ProviderConfig; sandbox uses deterministic stubs.
    """

    RETAILERS = ["Shoprite", "Checkers", "Usave", "Boxer", "Pick n Pay", "Other Pay@ merchants"]
    VOUCHER_EXPIRY_DAYS = 3
    PROVIDER = "pay_at"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.api_base_url = self.config.get("api_base_url")
        self.merchant_id = self.config.get("merchant_id")
        self.is_live = bool(self.api_base_url and self.merchant_id)

    @property
    def provider_code(self) -> str:
        return self.PROVIDER

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        if self.is_live:
            return self._generate_live_reference(request)
        return self._generate_stub_reference(request)

    def _generate_stub_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        ref = generate_reference_number(self.PROVIDER, request.transfer_reference)
        voucher = generate_voucher_number("PA")
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
            message="Present this voucher at any Pay@ participating retailer",
            metadata={
                "retailers": self.RETAILERS,
                "mode": "sandbox",
                "provider": self.PROVIDER,
                "amount_zar": str(request.amount),
            },
        )

    def _generate_live_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        # TODO: POST {api_base_url}/vouchers when Pay@ credentials are configured
        logger.info("Pay@ live API not yet connected — using sandbox voucher for %s", request.transfer_reference)
        result = self._generate_stub_reference(request)
        result.metadata = {**(result.metadata or {}), "mode": "api_fallback"}
        return result

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        return PaymentStatusResult(reference_number=reference_number, status="awaiting_payment")

    def process_webhook(self, payload: dict) -> WebhookResult:
        event = payload.get("event_type") or payload.get("type") or payload.get("status")
        ref = payload.get("reference") or payload.get("reference_number") or payload.get("payment_reference")

        if event in ("payment.received", "payment_received", "paid", "PAID") and ref:
            return WebhookResult(
                success=True,
                reference_number=str(ref),
                status="paid",
                raw_payload=payload,
            )
        if event in ("payment.expired", "expired") and ref:
            return WebhookResult(success=True, reference_number=str(ref), status="expired", raw_payload=payload)

        return WebhookResult(success=False, raw_payload=payload)

    def validate_credentials(self) -> bool:
        return self.is_live

    def get_api_status(self) -> dict[str, Any]:
        return {
            "provider": self.PROVIDER,
            "mode": "live" if self.is_live else "sandbox",
            "api_base_url": self.api_base_url,
            "merchant_configured": bool(self.merchant_id),
        }
