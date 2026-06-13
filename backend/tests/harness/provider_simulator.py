"""Simulate payment/remittance provider API responses for integration tests."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class ProviderSimResponse:
    success: bool
    reference: str
    status: str
    raw: dict


class ProviderSimulator:
    def __init__(self, provider_code: str = "pay_at"):
        self.provider_code = provider_code

    def create_payment_intent(self, amount: str, reference: str) -> ProviderSimResponse:
        return ProviderSimResponse(
            success=True,
            reference=reference,
            status="pending",
            raw={
                "provider": self.provider_code,
                "amount": amount,
                "reference": reference,
                "created_at": datetime.now(UTC).isoformat(),
            },
        )

    def confirm_payment(self, reference: str) -> ProviderSimResponse:
        return ProviderSimResponse(
            success=True,
            reference=reference,
            status="paid",
            raw={"provider": self.provider_code, "reference": reference, "status": "paid"},
        )

    def disburse_transfer(self, reference: str, corridor: str = "ZA-GH") -> ProviderSimResponse:
        return ProviderSimResponse(
            success=True,
            reference=reference,
            status="disbursed",
            raw={
                "provider": self.provider_code,
                "reference": reference,
                "corridor": corridor,
                "status": "disbursed",
            },
        )
