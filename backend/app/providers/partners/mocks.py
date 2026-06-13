import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.providers.partners.base import PartnerProvider, PartnerQuote, PartnerStatusResult, PartnerTransferResult

_CORRIDOR_RATES = {
    "ZA-GH": Decimal("0.7344"),
    "ZA-ZW": Decimal("18.5"),
    "ZA-ZM": Decimal("1.35"),
    "ZA-KE": Decimal("7.2"),
    "ZA-NG": Decimal("42.0"),
    "ZA-UG": Decimal("195.0"),
}

_CORRIDOR_CURRENCIES = {
    "ZA-GH": "GHS",
    "ZA-ZW": "ZWL",
    "ZA-ZM": "ZMW",
    "ZA-KE": "KES",
    "ZA-NG": "NGN",
    "ZA-UG": "UGX",
}


class _MockPartner(PartnerProvider):
    def __init__(self, code: str):
        self._code = code

    @property
    def provider_code(self) -> str:
        return self._code

    def quote(
        self,
        *,
        corridor: str,
        send_amount: Decimal,
        source_currency: str = "ZAR",
        destination_currency: str | None = None,
    ) -> PartnerQuote:
        dest = destination_currency or _CORRIDOR_CURRENCIES.get(corridor, "GHS")
        rate = _CORRIDOR_RATES.get(corridor, Decimal("0.72"))
        fee = max(Decimal("49.00"), send_amount * Decimal("0.015"))
        payout = (send_amount * rate).quantize(Decimal("0.01"))
        return PartnerQuote(
            provider_code=self._code,
            corridor=corridor,
            source_currency=source_currency,
            destination_currency=dest,
            send_amount=send_amount,
            fee_amount=fee,
            fx_rate=rate,
            payout_amount=payout,
            quote_reference=f"Q-{uuid.uuid4().hex[:12].upper()}",
            expires_at=(datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
        )

    def create_transfer(
        self,
        *,
        corridor: str,
        send_amount: Decimal,
        beneficiary_ref: str,
        customer_ref: str,
    ) -> PartnerTransferResult:
        ref = f"{self._code[:3].upper()}-{uuid.uuid4().hex[:10].upper()}"
        return PartnerTransferResult(
            provider_code=self._code,
            provider_reference=ref,
            status="submitted",
            message=f"Mock transfer created for {corridor} (no real money movement)",
        )

    def get_status(self, provider_reference: str) -> PartnerStatusResult:
        return PartnerStatusResult(
            provider_code=self._code,
            provider_reference=provider_reference,
            status="processing",
            raw={"mock": True, "checked_at": datetime.now(UTC).isoformat()},
        )


class FlutterwaveProvider(_MockPartner):
    def __init__(self):
        super().__init__("flutterwave")


class MukuruProvider(_MockPartner):
    def __init__(self):
        super().__init__("mukuru")


class OnafriqProvider(_MockPartner):
    def __init__(self):
        super().__init__("onafriq")


class VeenguProvider(_MockPartner):
    def __init__(self):
        super().__init__("veengu")
