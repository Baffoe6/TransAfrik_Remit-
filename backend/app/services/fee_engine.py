from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.fee_rule import FeeRule


def calculate_fee(
    db: Session,
    amount_zar: Decimal,
    *,
    destination_country: str | None = None,
    payment_method_id: int | None = None,
    provider_id: int | None = None,
) -> tuple[Decimal, FeeRule | None]:
    rules = (
        db.query(FeeRule)
        .filter(FeeRule.is_active.is_(True))
        .order_by(FeeRule.priority.desc(), FeeRule.min_amount_zar.desc())
        .all()
    )

    for rule in rules:
        if amount_zar < rule.min_amount_zar:
            continue
        if rule.max_amount_zar is not None and amount_zar > rule.max_amount_zar:
            continue
        if rule.destination_country and destination_country and rule.destination_country != destination_country:
            continue
        if rule.payment_method_id and payment_method_id and rule.payment_method_id != payment_method_id:
            continue
        if rule.provider_id and provider_id and rule.provider_id != provider_id:
            continue

        if rule.fee_type == "percentage":
            fee = (amount_zar * rule.fee_value / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            fee = rule.fee_value
        return fee, rule

    return Decimal("50.00"), None
