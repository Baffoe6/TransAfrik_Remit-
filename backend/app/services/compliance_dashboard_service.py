"""Compliance dashboard metrics."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.compliance import CustomerRiskProfile, EnhancedDueDiligenceCase
from app.models.customer_profile import CustomerProfile
from app.models.enums import EddStatus, KycStatus, TransferStatus
from app.models.kyc_document import KycDocument
from app.models.transfer import Transfer


def get_compliance_dashboard(db: Session) -> dict:
    now = datetime.now(UTC)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)

    kyc_queue = (
        db.query(func.count(CustomerProfile.id))
        .filter(CustomerProfile.kyc_status == KycStatus.PENDING)
        .scalar()
        or 0
    )
    high_risk = (
        db.query(func.count(CustomerRiskProfile.id))
        .filter(CustomerRiskProfile.risk_level.in_(["high", "very_high"]))
        .scalar()
        or 0
    )
    high_risk_transfers = (
        db.query(func.count(Transfer.id))
        .filter(Transfer.risk_score >= 70, Transfer.status == TransferStatus.COMPLIANCE_REVIEW)
        .scalar()
        or 0
    )
    daily_volume = (
        db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0))
        .filter(Transfer.created_at >= day_start)
        .scalar()
    )
    monthly_volume = (
        db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0))
        .filter(Transfer.created_at >= month_start)
        .scalar()
    )
    edd_open = (
        db.query(func.count(EnhancedDueDiligenceCase.id))
        .filter(EnhancedDueDiligenceCase.status.in_([EddStatus.OPEN, EddStatus.IN_REVIEW]))
        .scalar()
        or 0
    )

    from app.models.user import User

    kyc_items = (
        db.query(CustomerProfile, User)
        .join(User, User.id == CustomerProfile.user_id)
        .filter(CustomerProfile.kyc_status == KycStatus.PENDING)
        .order_by(CustomerProfile.updated_at.desc())
        .limit(20)
        .all()
    )

    return {
        "kyc_queue_count": kyc_queue,
        "kyc_queue": [
            {
                "user_id": p.user_id,
                "email": u.email,
                "mobile_number": u.mobile_number,
                "name": f"{p.first_name} {p.last_name}",
                "kyc_status": p.kyc_status.value if hasattr(p.kyc_status, "value") else p.kyc_status,
            }
            for p, u in kyc_items
        ],
        "high_risk_customers": high_risk,
        "high_risk_transactions": high_risk_transfers,
        "edd_open_cases": edd_open,
        "daily_volume_zar": str(Decimal(str(daily_volume))),
        "monthly_volume_zar": str(Decimal(str(monthly_volume))),
    }


def export_compliance_csv(db: Session) -> str:
    import csv
    import io

    from app.models.user import User

    rows = (
        db.query(Transfer, User)
        .join(User, User.id == Transfer.user_id)
        .filter(Transfer.risk_score >= 50)
        .order_by(Transfer.created_at.desc())
        .limit(1000)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["reference", "customer_email", "status", "risk_score", "send_amount_zar", "created_at"])
    for t, u in rows:
        writer.writerow([
            t.reference,
            u.email,
            t.status.value if hasattr(t.status, "value") else t.status,
            t.risk_score,
            str(t.send_amount_zar),
            t.created_at.isoformat() if t.created_at else "",
        ])
    return output.getvalue()
