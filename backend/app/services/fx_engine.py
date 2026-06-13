from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.enums import FxMarkupType, FxRateSourceType
from app.models.fx import FxMarkupRule, FxRateSource
from app.services.exchange_rate_engine import get_rate_for_date


class RateSourceAdapter(ABC):
    @abstractmethod
    def fetch_rate(self, db: Session, *, from_currency: str, to_currency: str, on_date: date) -> Decimal | None:
        pass


class ManualRateSource(RateSourceAdapter):
    def fetch_rate(self, db: Session, *, from_currency: str, to_currency: str, on_date: date) -> Decimal | None:
        record = get_rate_for_date(db, from_currency=from_currency, to_currency=to_currency, on_date=on_date)
        return record.rate if record else None


class ApiRateSource(RateSourceAdapter):
    """Placeholder for external FX API feeds."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def fetch_rate(self, db: Session, *, from_currency: str, to_currency: str, on_date: date) -> Decimal | None:
        # TODO: fetch from configured API (e.g. openexchangerates, xe.com partner API)
        return ManualRateSource().fetch_rate(db, from_currency=from_currency, to_currency=to_currency, on_date=on_date)


def _get_adapter(source_type: FxRateSourceType, config: dict | None) -> RateSourceAdapter:
    if source_type == FxRateSourceType.API:
        return ApiRateSource(config)
    return ManualRateSource()


def apply_markup(db: Session, base_rate: Decimal, *, from_currency: str = "ZAR", to_currency: str = "GHS") -> Decimal:
    rules = (
        db.query(FxMarkupRule)
        .filter(
            FxMarkupRule.is_active.is_(True),
            FxMarkupRule.from_currency == from_currency,
            FxMarkupRule.to_currency == to_currency,
        )
        .order_by(FxMarkupRule.priority.desc())
        .all()
    )
    rate = base_rate
    for rule in rules:
        if rule.markup_type == FxMarkupType.PERCENTAGE:
            rate = rate * (Decimal("1") + rule.markup_value / Decimal("100"))
        else:
            rate = rate + rule.markup_value
    return rate.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def get_effective_fx_rate(
    db: Session,
    *,
    from_currency: str = "ZAR",
    to_currency: str = "GHS",
    on_date: date | None = None,
) -> tuple[Decimal, dict]:
    on_date = on_date or date.today()
    sources = (
        db.query(FxRateSource)
        .filter(FxRateSource.is_active.is_(True))
        .order_by(FxRateSource.priority.desc())
        .all()
    )
    base_rate = None
    source_used = "manual"
    if not sources:
        base_rate = ManualRateSource().fetch_rate(db, from_currency=from_currency, to_currency=to_currency, on_date=on_date)
    for src in sources:
        adapter = _get_adapter(
            src.source_type if hasattr(src.source_type, "value") else FxRateSourceType(src.source_type),
            src.config,
        )
        base_rate = adapter.fetch_rate(db, from_currency=from_currency, to_currency=to_currency, on_date=on_date)
        if base_rate is not None:
            source_used = src.code
            break

    if base_rate is None:
        raise ValueError("No FX rate available from configured sources")

    effective = apply_markup(db, base_rate, from_currency=from_currency, to_currency=to_currency)
    return effective, {"base_rate": str(base_rate), "effective_rate": str(effective), "source": source_used}
