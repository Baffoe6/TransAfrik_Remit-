from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.enums import TransferStatus
from app.models.payment_method import PaymentMethod
from app.models.transfer import Transfer


def get_analytics_dashboard(db: Session) -> dict:
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today_start.replace(day=1)

    daily_volume = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.created_at >= today_start,
        Transfer.status.notin_([TransferStatus.FAILED, TransferStatus.EXPIRED]),
    ).scalar()

    monthly_volume = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.created_at >= month_start,
        Transfer.status == TransferStatus.COMPLETED,
    ).scalar()

    daily_revenue = db.query(func.coalesce(func.sum(Transfer.fee_zar), 0)).filter(
        Transfer.created_at >= today_start,
        Transfer.status == TransferStatus.COMPLETED,
    ).scalar()

    monthly_revenue = db.query(func.coalesce(func.sum(Transfer.fee_zar), 0)).filter(
        Transfer.created_at >= month_start,
        Transfer.status == TransferStatus.COMPLETED,
    ).scalar()

    country_stats = (
        db.query(
            Beneficiary.country,
            func.count(Transfer.id),
            func.coalesce(func.sum(Transfer.send_amount_zar), 0),
        )
        .join(Transfer, Transfer.beneficiary_id == Beneficiary.id)
        .group_by(Beneficiary.country)
        .all()
    )

    payment_stats = (
        db.query(
            PaymentMethod.name,
            func.count(Transfer.id),
            func.coalesce(func.sum(Transfer.send_amount_zar), 0),
        )
        .join(Transfer, Transfer.payment_method_id == PaymentMethod.id)
        .group_by(PaymentMethod.name)
        .all()
    )

    by_status = db.query(Transfer.status, func.count(Transfer.id)).group_by(Transfer.status).all()

    return {
        "daily_volume_zar": str(daily_volume),
        "monthly_volume_zar": str(monthly_volume),
        "daily_revenue_zar": str(daily_revenue),
        "monthly_revenue_zar": str(monthly_revenue),
        "transfers_by_country": [
            {"country": c, "count": cnt, "volume_zar": str(vol)} for c, cnt, vol in country_stats
        ],
        "transfers_by_payment_method": [
            {"method": m, "count": cnt, "volume_zar": str(vol)} for m, cnt, vol in payment_stats
        ],
        "transfers_by_status": {s.value if hasattr(s, "value") else s: c for s, c in by_status},
        "completed_today": db.query(func.count(Transfer.id)).filter(
            Transfer.status == TransferStatus.COMPLETED,
            Transfer.completed_at >= today_start,
        ).scalar() or 0,
    }
