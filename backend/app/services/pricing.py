from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.services.corridor_currency import resolve_corridor_currencies, resolve_corridor_delivery
from app.services.fee_engine import calculate_fee_included, calculate_provider_cost
from app.services.fx_engine import get_effective_fx_rate


def calculate_fx_margin_zar(
    send_amount_zar: Decimal,
    base_rate: Decimal,
    effective_rate: Decimal,
) -> Decimal:
    if base_rate <= 0:
        return Decimal("0")
    margin = send_amount_zar * (base_rate - effective_rate) / base_rate
    return margin.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_transfer_amounts(
    db: Session,
    amount_to_pay_zar: Decimal,
    *,
    destination_country: str = "GH",
    payment_method_id: int | None = None,
    provider_id: int | None = None,
    on_date: date | None = None,
) -> dict:
    """Fee-inclusive pricing: customer amount is final (no checkout surcharges)."""
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

    fee_result = calculate_fee_included(
        db,
        amount_to_pay_zar,
        destination_country=destination_country,
        payment_method_id=payment_method_id,
        provider_id=provider_id,
        source_country="ZA",
    )
    send_amount_zar = fee_result.net_send_zar
    fee = fee_result.fee_zar
    receive_amount = (send_amount_zar * effective_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    delivery = resolve_corridor_delivery(destination_country)

    base_rate = Decimal(fx_meta.get("base_rate", effective_rate))
    markup_pct = Decimal("0")
    if base_rate > 0:
        markup_pct = ((effective_rate - base_rate) / base_rate * Decimal("100")).quantize(Decimal("0.01"))

    provider_cost_zar = calculate_provider_cost(send_amount_zar, corridor_rule=fee_result.corridor_rule)
    fx_margin_zar = calculate_fx_margin_zar(send_amount_zar, base_rate, effective_rate)
    net_revenue_zar = (fee + fx_margin_zar - provider_cost_zar).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    tier = fee_result.corridor_tier
    return {
        "amount_to_pay_zar": amount_to_pay_zar,
        "send_amount_zar": send_amount_zar,
        "fee_zar": fee,
        "exchange_rate": effective_rate,
        "receive_amount_ghs": receive_amount,
        "receive_amount": receive_amount,
        "total_amount_zar": amount_to_pay_zar,
        "from_currency": source_currency,
        "to_currency": dest_currency,
        "corridor_code": corridor_code,
        "customer_rate": effective_rate,
        "delivery_method": delivery["delivery_method"],
        "estimated_delivery": delivery["estimated_delivery"],
        "corridor_fee_tier_id": tier.id if tier else None,
        "fee_tier_label": tier.label if tier else None,
        "provider_cost_zar": provider_cost_zar,
        "fx_margin_zar": fx_margin_zar,
        "net_revenue_zar": net_revenue_zar,
        # Internal — admin / settlement only (not exposed on customer quote schema)
        "base_rate": base_rate,
        "markup_percentage": markup_pct,
        "provider": fx_meta.get("source", "manual"),
        "fx_metadata": fx_meta,
    }


def build_customer_quote(amounts: dict) -> dict:
    """Strip internal profitability fields from a pricing result."""
    return {
        "amount_to_pay_zar": amounts["amount_to_pay_zar"],
        "fee_zar": amounts["fee_zar"],
        "exchange_rate": amounts["exchange_rate"],
        "customer_rate": amounts["customer_rate"],
        "receive_amount": amounts["receive_amount"],
        "receive_amount_ghs": amounts["receive_amount_ghs"],
        "total_amount_zar": amounts["total_amount_zar"],
        "from_currency": amounts["from_currency"],
        "to_currency": amounts["to_currency"],
        "corridor_code": amounts["corridor_code"],
        "delivery_method": amounts["delivery_method"],
        "estimated_delivery": amounts["estimated_delivery"],
    }
