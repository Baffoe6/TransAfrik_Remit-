from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.services.fee_engine import calculate_fee
from app.services.fx_engine import get_effective_fx_rate


def calculate_transfer_amounts(
    db: Session,
    send_amount_zar: Decimal,
    *,
    destination_country: str = "GH",
    payment_method_id: int | None = None,
    provider_id: int | None = None,
    on_date: date | None = None,
) -> dict[str, Decimal]:
    try:
        effective_rate, fx_meta = get_effective_fx_rate(
            db, from_currency="ZAR", to_currency="GHS", on_date=on_date
        )
    except ValueError as e:
        raise ValueError("No active exchange rate configured for the selected date") from e

    fee, _ = calculate_fee(
        db,
        send_amount_zar,
        destination_country=destination_country,
        payment_method_id=payment_method_id,
        provider_id=provider_id,
    )
    receive_amount = (send_amount_zar * effective_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = send_amount_zar + fee

    return {
        "send_amount_zar": send_amount_zar,
        "fee_zar": fee,
        "exchange_rate": effective_rate,
        "receive_amount_ghs": receive_amount,
        "total_amount_zar": total,
        "fx_metadata": fx_meta,
    }
