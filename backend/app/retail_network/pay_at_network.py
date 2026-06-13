from typing import Any

from app.payment_providers.pay_at import PayAtProvider
from app.payment_providers.base import PaymentReferenceRequest, PaymentReferenceResult, PaymentStatusResult, WebhookResult
from app.retail_network.base import RetailNetworkInfo, RetailPaymentNetwork


class PayAtNetwork(RetailPaymentNetwork):
    def __init__(self, config: dict[str, Any] | None = None):
        self._provider = PayAtProvider(config)

    @property
    def network_code(self) -> str:
        return "pay_at"

    def get_network_info(self) -> RetailNetworkInfo:
        return RetailNetworkInfo(
            code="pay_at",
            name="Pay@",
            network_type="voucher",
            supported_channels=["shoprite", "checkers", "pick_n_pay", "boxer", "usave"],
        )

    def generate_voucher(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        return self._provider.generate_reference(request)

    def check_status(self, reference_number: str) -> PaymentStatusResult:
        return self._provider.check_payment_status(reference_number)

    def process_webhook(self, payload: dict) -> WebhookResult:
        return self._provider.process_webhook(payload)
