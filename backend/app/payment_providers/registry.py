from app.payment_providers.base import PaymentProvider
from app.payment_providers.easy_pay import EasyPayProvider
from app.payment_providers.eft import EftProvider
from app.payment_providers.instant_eft import (
    OzowProvider,
    PayFastProvider,
    PeachPaymentsProvider,
    StitchProvider,
)
from app.payment_providers.pay_at import PayAtProvider

_RETAIL_NETWORK_CODES = frozenset({"kazang", "flash", "shoprite", "pick_n_pay"})


class _RetailNetworkAdapter(PaymentProvider):
    def __init__(self, code: str, config: dict | None = None):
        from app.retail_network.registry import get_retail_network

        self._network = get_retail_network(code, config)

    @property
    def provider_code(self) -> str:
        return self._network.network_code

    def generate_reference(self, request):
        return self._network.generate_voucher(request)

    def check_payment_status(self, reference_number: str):
        return self._network.check_status(reference_number)

    def process_webhook(self, payload: dict):
        return self._network.process_webhook(payload)


_PAYMENT_PROVIDERS: dict[str, type[PaymentProvider]] = {
    "pay_at": PayAtProvider,
    "easy_pay": EasyPayProvider,
    "eft": EftProvider,
    "stitch": StitchProvider,
    "ozow": OzowProvider,
    "peach_payments": PeachPaymentsProvider,
    "payfast": PayFastProvider,
}


def get_payment_provider(provider_class: str, config: dict | None = None) -> PaymentProvider:
    if provider_class in _RETAIL_NETWORK_CODES:
        return _RetailNetworkAdapter(provider_class, config)
    provider_cls = _PAYMENT_PROVIDERS.get(provider_class)
    if not provider_cls:
        raise ValueError(f"Unknown payment provider class: {provider_class}")
    if config is not None and provider_class in ("pay_at", "easy_pay"):
        return provider_cls(config=config)
    return provider_cls()
