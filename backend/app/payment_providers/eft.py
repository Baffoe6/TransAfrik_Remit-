from datetime import UTC, datetime, timedelta

from app.payment_providers.base import (
    PaymentProvider,
    PaymentReferenceRequest,
    PaymentReferenceResult,
    PaymentStatusResult,
    WebhookResult,
)


class EftProvider(PaymentProvider):
    """EFT / cash deposit — manual verification via proof of payment upload."""

    BANK_DETAILS = {
        "bank_name": "FNB",
        "account_name": "IPAYGO (Pty) Ltd",
        "account_number": "62812345678",
        "branch_code": "250655",
        "account_type": "Business Cheque",
        "reference_instruction": "Use the payment reference exactly as shown",
    }

    @property
    def provider_code(self) -> str:
        return "eft"

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        ref = f"EFT-{request.transfer_reference}"
        return PaymentReferenceResult(
            success=True,
            reference_number=ref,
            expiry_date=(datetime.now(UTC) + timedelta(days=7)).date(),
            banking_instructions={
                **self.BANK_DETAILS,
                "payment_reference": ref,
                "amount": str(request.amount),
                "currency": request.currency,
            },
            message="Pay via EFT or cash deposit and upload proof of payment",
            metadata={"requires_proof_upload": True},
        )

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        return PaymentStatusResult(reference_number=reference_number, status="awaiting_payment")

    def process_webhook(self, payload: dict) -> WebhookResult:
        return WebhookResult(success=False, raw_payload=payload)
