"""
API-ready provider interface extensions for Phase 2.

These extend the stub providers with explicit API contract methods
that will be implemented when live credentials are configured.
"""

from abc import abstractmethod
from typing import Any

from app.payment_providers.base import PaymentProvider, PaymentReferenceRequest, PaymentReferenceResult, PaymentStatusResult


class ApiReadyPaymentProvider(PaymentProvider):
    """Extended payment provider interface for live API integrations."""

    @abstractmethod
    def validate_credentials(self) -> bool:
        pass

    @abstractmethod
    def get_api_status(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def cancel_reference(self, reference_number: str) -> PaymentReferenceResult:
        pass


class PayAtApiProvider(ApiReadyPaymentProvider):
    """Pay@ API-ready interface — extends voucher stub."""

    @property
    def provider_code(self) -> str:
        return "pay_at"

    def validate_credentials(self) -> bool:
        return False

    def get_api_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "provider": "pay_at"}

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        from app.payment_providers.pay_at import PayAtProvider
        return PayAtProvider().generate_reference(request)

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        from app.payment_providers.pay_at import PayAtProvider
        return PayAtProvider().check_payment_status(reference_number)

    def process_webhook(self, payload: dict) -> Any:
        from app.payment_providers.base import WebhookResult
        return WebhookResult(success=False, raw_payload=payload)

    def cancel_reference(self, reference_number: str) -> PaymentReferenceResult:
        return PaymentReferenceResult(success=False, reference_number=reference_number, message="Pay@ API not configured")


class EasyPayApiProvider(ApiReadyPaymentProvider):
    @property
    def provider_code(self) -> str:
        return "easy_pay"

    def validate_credentials(self) -> bool:
        return False

    def get_api_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "provider": "easy_pay"}

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        from app.payment_providers.easy_pay import EasyPayProvider
        return EasyPayProvider().generate_reference(request)

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        from app.payment_providers.easy_pay import EasyPayProvider
        return EasyPayProvider().check_payment_status(reference_number)

    def process_webhook(self, payload: dict) -> Any:
        from app.payment_providers.base import WebhookResult
        return WebhookResult(success=False, raw_payload=payload)

    def cancel_reference(self, reference_number: str) -> PaymentReferenceResult:
        return PaymentReferenceResult(success=False, reference_number=reference_number, message="EasyPay API not configured")
