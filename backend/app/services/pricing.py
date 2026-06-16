from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.services.corridor_currency import resolve_corridor_currencies
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
) -> dict:
    source_currency, dest_currency, corridor_code = resolve_corridor_currencies(
        db, destination_country=destination_country
    )

    try:
        effective_rate, fx_meta = get_effective_fx_rate(
            db, from_currency=source_currency, to_currency=dest_currency, on_date=on_date
        )
    except ValueError as e:
        raise ValueError(
            f"No active exchange rate configured for {source_currency}→{dest_currency}"
        ) from e

    fee, _ = calculate_fee(
        db,
        send_amount_zar,
        destination_country=destination_country,
        payment_method_id=payment_method_id,
        provider_id=provider_id,
    )
    receive_amount = (send_amount_zar * effective_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = send_amount_zar + fee

    base_rate = Decimal(fx_meta.get("base_rate", effective_rate))
    markup_pct = Decimal("0")
    if base_rate > 0:
        markup_pct = ((effective_rate - base_rate) / base_rate * Decimal("100")).quantize(Decimal("0.01"))

    return {
        "send_amount_zar": send_amount_zar,
        "fee_zar": fee,
        "exchange_rate": effective_rate,
        "receive_amount_ghs": receive_amount,
        "receive_amount": receive_amount,
        "total_amount_zar": total,
        "from_currency": source_currency,
        "to_currency": dest_currency,
        "corridor_code": corridor_code,
        "base_rate": base_rate,
        "markup_percentage": markup_pct,
        "customer_rate": effective_rate,
        "provider": fx_meta.get("source", "manual"),
        "fx_metadata": fx_meta,
    }
