from typing import Any

from app.payment_providers.easy_pay import EasyPayProvider
from app.payment_providers.base import PaymentReferenceRequest, PaymentReferenceResult, PaymentStatusResult, WebhookResult
from app.retail_network.base import RetailNetworkInfo, RetailPaymentNetwork


class EasyPayNetwork(RetailPaymentNetwork):
    def __init__(self, config: dict[str, Any] | None = None):
        self._provider = EasyPayProvider(config)

    @property
    def network_code(self) -> str:
        return "easy_pay"

    def get_network_info(self) -> RetailNetworkInfo:
        return RetailNetworkInfo(code="easy_pay", name="EasyPay", network_type="voucher", supported_channels=["retail_outlets"])

    def generate_voucher(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        return self._provider.generate_reference(request)

    def check_status(self, reference_number: str) -> PaymentStatusResult:
        return self._provider.check_payment_status(reference_number)

    def process_webhook(self, payload: dict) -> WebhookResult:
        return self._provider.process_webhook(payload)
