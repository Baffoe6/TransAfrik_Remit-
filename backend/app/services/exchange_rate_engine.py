from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.exchange_rate import ExchangeRate, ExchangeRateHistory


def get_rate_for_date(
    db: Session,
    *,
    from_currency: str = "ZAR",
    to_currency: str = "GHS",
    on_date: date | None = None,
) -> ExchangeRate | None:
    on_date = on_date or date.today()
    return (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.from_currency == from_currency,
            ExchangeRate.to_currency == to_currency,
            ExchangeRate.is_active.is_(True),
            ExchangeRate.effective_from <= on_date,
            (ExchangeRate.effective_to.is_(None)) | (ExchangeRate.effective_to >= on_date),
        )
        .order_by(ExchangeRate.effective_from.desc())
        .first()
    )


def create_exchange_rate(
    db: Session,
    *,
    from_currency: str,
    to_currency: str,
    rate: Decimal,
    effective_from: date,
    effective_to: date | None,
    created_by: int | None,
    change_reason: str | None = None,
) -> ExchangeRate:
    db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == from_currency,
        ExchangeRate.to_currency == to_currency,
        ExchangeRate.is_active.is_(True),
    ).update({ExchangeRate.is_active: False})

    record = ExchangeRate(
        from_currency=from_currency,
        to_currency=to_currency,
        rate=rate,
        effective_from=effective_from,
        effective_to=effective_to,
        is_active=True,
        created_by=created_by,
    )
    db.add(record)
    db.flush()

    history = ExchangeRateHistory(
        exchange_rate_id=record.id,
        from_currency=from_currency,
        to_currency=to_currency,
        rate=rate,
        effective_from=effective_from,
        effective_to=effective_to,
        changed_by=created_by,
        change_reason=change_reason,
    )
    db.add(history)
    db.flush()
    return record


def list_rate_history(db: Session, limit: int = 50) -> list[ExchangeRateHistory]:
    return db.query(ExchangeRateHistory).order_by(ExchangeRateHistory.created_at.desc()).limit(limit).all()
