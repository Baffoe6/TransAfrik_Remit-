"""Resolve corridor currencies for pricing and quotes."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.corridor import Corridor

# Fallback when corridor row is missing (e.g. before seed)
COUNTRY_CURRENCY_MAP: dict[str, tuple[str, str]] = {
    "GH": ("ZAR", "GHS"),
    "ZW": ("ZAR", "USD"),
    "ZM": ("ZAR", "ZMW"),
    "KE": ("ZAR", "KES"),
    "NG": ("ZAR", "NGN"),
    "UG": ("ZAR", "UGX"),
    "GB": ("GBP", "GHS"),
    "US": ("USD", "GHS"),
    "EU": ("EUR", "GHS"),
}

# Approximate demo rates when DB has no row (seed/migration should populate real rates)
FALLBACK_RATES: dict[tuple[str, str], Decimal] = {
    ("ZAR", "GHS"): Decimal("0.72"),
    ("ZAR", "KES"): Decimal("7.15"),
    ("ZAR", "NGN"): Decimal("42.50"),
    ("ZAR", "UGX"): Decimal("195.00"),
    ("ZAR", "ZMW"): Decimal("1.35"),
    ("ZAR", "USD"): Decimal("0.054"),
    ("ZAR", "ZWL"): Decimal("18.50"),
    ("GBP", "GHS"): Decimal("15.80"),
    ("USD", "GHS"): Decimal("12.50"),
    ("EUR", "GHS"): Decimal("13.60"),
}


def resolve_corridor_currencies(
    db: Session,
    *,
    destination_country: str,
    source_country: str = "ZA",
) -> tuple[str, str, str | None]:
    """Return (source_currency, destination_currency, corridor_code)."""
    corridor = (
        db.query(Corridor)
        .filter(
            Corridor.destination_country == destination_country.upper(),
            Corridor.source_country == source_country.upper(),
        )
        .order_by(Corridor.priority.desc())
        .first()
    )
    if corridor:
        source = "ZAR" if corridor.source_country == "ZA" else corridor.source_country
        return source, corridor.destination_currency, corridor.code

    pair = COUNTRY_CURRENCY_MAP.get(destination_country.upper())
    if pair:
        return pair[0], pair[1], None

    return "ZAR", "GHS", None
