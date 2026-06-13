from app.payment_providers.base import (
    PaymentProvider,
    PaymentReferenceRequest,
    PaymentReferenceResult,
    PaymentStatusResult,
    WebhookResult,
)


class InstantEftProvider(PaymentProvider):
    """Future-ready instant EFT / card gateway stub."""

    @property
    def provider_code(self) -> str:
        return "instant_eft"

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        ref = f"INST-{request.transfer_reference}"
        return PaymentReferenceResult(
            success=True,
            reference_number=ref,
            message="Instant payment gateway not yet integrated — stub reference generated",
            metadata={"gateway_url": None, "mode": "stub"},
        )

    def initiate_payment(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        result = self.generate_reference(request)
        result.metadata = {**(result.metadata or {}), "redirect_url": None}
        return result

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        return PaymentStatusResult(reference_number=reference_number, status="not_implemented")

    def process_webhook(self, payload: dict) -> WebhookResult:
        return WebhookResult(success=False, raw_payload=payload)


class StitchProvider(InstantEftProvider):
    @property
    def provider_code(self) -> str:
        return "stitch"


class OzowProvider(InstantEftProvider):
    @property
    def provider_code(self) -> str:
        return "ozow"


class PeachPaymentsProvider(InstantEftProvider):
    @property
    def provider_code(self) -> str:
        return "peach_payments"


class PayFastProvider(InstantEftProvider):
    @property
    def provider_code(self) -> str:
        return "payfast"
