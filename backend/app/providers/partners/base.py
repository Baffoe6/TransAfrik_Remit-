from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PartnerQuote:
    provider_code: str
    corridor: str
    source_currency: str
    destination_currency: str
    send_amount: Decimal
    fee_amount: Decimal
    fx_rate: Decimal
    payout_amount: Decimal
    quote_reference: str
    expires_at: str | None = None


@dataclass
class PartnerTransferResult:
    provider_code: str
    provider_reference: str
    status: str
    message: str | None = None


@dataclass
class PartnerStatusResult:
    provider_code: str
    provider_reference: str
    status: str
    raw: dict | None = None


class PartnerProvider(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def quote(
        self,
        *,
        corridor: str,
        send_amount: Decimal,
        source_currency: str = "ZAR",
        destination_currency: str = "GHS",
    ) -> PartnerQuote:
        pass

    @abstractmethod
    def create_transfer(
        self,
        *,
        corridor: str,
        send_amount: Decimal,
        beneficiary_ref: str,
        customer_ref: str,
    ) -> PartnerTransferResult:
        pass

    @abstractmethod
    def get_status(self, provider_reference: str) -> PartnerStatusResult:
        pass
