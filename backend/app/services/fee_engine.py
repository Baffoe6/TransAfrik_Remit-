from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session, joinedload

from app.models.corridor_fee import CorridorFeeRule, CorridorFeeTier
from app.models.fee_rule import FeeRule


def resolve_corridor_fee_tier(
    db: Session,
    amount_to_pay_zar: Decimal,
    *,
    destination_country: str | None = None,
    source_country: str = "ZA",
) -> tuple[Decimal, CorridorFeeTier, CorridorFeeRule] | None:
    """Select the matching tier for a fee-inclusive amount on a corridor."""
    if not destination_country:
        return None

    dest = destination_country.upper()
    corridor_code = f"{source_country.upper()}-{dest}"

    rule = (
        db.query(CorridorFeeRule)
        .options(joinedload(CorridorFeeRule.tiers))
        .filter(
            CorridorFeeRule.is_active.is_(True),
            CorridorFeeRule.destination_country == dest,
        )
        .order_by(CorridorFeeRule.priority.desc(), CorridorFeeRule.id.asc())
        .all()
    )

    matched_rule = None
    for candidate in rule:
        if candidate.corridor_code == corridor_code or candidate.destination_country == dest:
            matched_rule = candidate
            break

    if not matched_rule:
        return None

    active_tiers = [t for t in matched_rule.tiers if t.is_active]
    active_tiers.sort(key=lambda t: t.min_amount_zar, reverse=True)

    for tier in active_tiers:
        if amount_to_pay_zar < tier.min_amount_zar:
            continue
        if tier.max_amount_zar is not None and amount_to_pay_zar > tier.max_amount_zar:
            continue
        return tier.fee_zar, tier, matched_rule

    return None


def calculate_fee(
    db: Session,
    amount_zar: Decimal,
    *,
    destination_country: str | None = None,
    payment_method_id: int | None = None,
    provider_id: int | None = None,
) -> tuple[Decimal, FeeRule | None]:
    """Legacy fee rules — used when no corridor tier applies."""
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


class FeeIncludedResult:
    __slots__ = ("fee_zar", "net_send_zar", "corridor_tier", "corridor_rule", "legacy_rule")

    def __init__(
        self,
        fee_zar: Decimal,
        net_send_zar: Decimal,
        *,
        corridor_tier: CorridorFeeTier | None = None,
        corridor_rule: CorridorFeeRule | None = None,
        legacy_rule: FeeRule | None = None,
    ):
        self.fee_zar = fee_zar
        self.net_send_zar = net_send_zar
        self.corridor_tier = corridor_tier
        self.corridor_rule = corridor_rule
        self.legacy_rule = legacy_rule


def calculate_fee_included(
    db: Session,
    amount_to_pay_zar: Decimal,
    *,
    destination_country: str | None = None,
    payment_method_id: int | None = None,
    provider_id: int | None = None,
    source_country: str = "ZA",
) -> FeeIncludedResult:
    """Derive fee and net send amount from a fee-inclusive amount to pay."""
    tier_match = resolve_corridor_fee_tier(
        db,
        amount_to_pay_zar,
        destination_country=destination_country,
        source_country=source_country,
    )

    if tier_match:
        fee, tier, rule = tier_match
        net_send = (amount_to_pay_zar - fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if net_send <= 0:
            raise ValueError("Amount too low to cover the transfer fee")
        return FeeIncludedResult(fee, net_send, corridor_tier=tier, corridor_rule=rule)

    fee, legacy_rule = calculate_fee(
        db,
        amount_to_pay_zar,
        destination_country=destination_country,
        payment_method_id=payment_method_id,
        provider_id=provider_id,
    )

    if legacy_rule and legacy_rule.fee_type == "percentage":
        net_send = (amount_to_pay_zar / (Decimal("1") + legacy_rule.fee_value / Decimal("100"))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        fee = (amount_to_pay_zar - net_send).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        net_send = (amount_to_pay_zar - fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if net_send <= 0:
        raise ValueError("Amount too low to cover the transfer fee")

    return FeeIncludedResult(fee, net_send, legacy_rule=legacy_rule)


def calculate_provider_cost(
    send_amount_zar: Decimal,
    *,
    corridor_rule: CorridorFeeRule | None = None,
) -> Decimal:
    if corridor_rule and corridor_rule.provider_cost_flat_zar is not None:
        return corridor_rule.provider_cost_flat_zar
    pct = corridor_rule.provider_cost_pct if corridor_rule else Decimal("1.5")
    return (send_amount_zar * pct / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
