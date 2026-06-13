"""Generic retail voucher network for Kazang, Flash, Shoprite, Pick n Pay."""

from typing import Any

from app.payment_providers.base import PaymentReferenceRequest, PaymentReferenceResult, PaymentStatusResult, WebhookResult
from app.payment_providers.voucher import default_expiry, generate_barcode_data, generate_qr_url, generate_reference_number, generate_voucher_number
from app.retail_network.base import RetailNetworkInfo, RetailPaymentNetwork


class GenericVoucherNetwork(RetailPaymentNetwork):
    def __init__(self, code: str, name: str, channels: list[str], config: dict[str, Any] | None = None):
        self._code = code
        self._name = name
        self._channels = channels
        self._config = config or {}

    @property
    def network_code(self) -> str:
        return self._code

    def get_network_info(self) -> RetailNetworkInfo:
        return RetailNetworkInfo(code=self._code, name=self._name, network_type="voucher", supported_channels=self._channels)

    def generate_voucher(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        ref = generate_reference_number(self._code, request.transfer_reference)
        voucher = generate_voucher_number(self._code[:2].upper())
        return PaymentReferenceResult(
            success=True,
            reference_number=ref,
            voucher_number=voucher,
            barcode_data=generate_barcode_data(self._code, ref, voucher, request.amount),
            qr_data=generate_qr_url(self._code, ref),
            expiry_date=default_expiry(3),
            message=f"Pay at {self._name} partner outlets",
            metadata={"network": self._code, "mode": "sandbox"},
        )

    def check_status(self, reference_number: str) -> PaymentStatusResult:
        return PaymentStatusResult(reference_number=reference_number, status="awaiting_payment")

    def process_webhook(self, payload: dict) -> WebhookResult:
        ref = payload.get("reference") or payload.get("reference_number")
        event = payload.get("event_type") or payload.get("status")
        if ref and event in ("paid", "payment_received", "SETTLED"):
            return WebhookResult(success=True, reference_number=str(ref), status="paid", raw_payload=payload)
        return WebhookResult(success=False, raw_payload=payload)
