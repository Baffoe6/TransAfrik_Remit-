"""Operations dashboard metrics."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer_profile import CustomerProfile
from app.models.enums import KycStatus, TransferStatus, UserRole
from app.models.transfer import Transfer
from app.models.user import User
from app.models.waitlist import WaitlistLead


def get_operations_dashboard(db: Session) -> dict:
    now = datetime.now(UTC)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)

    total_customers = (
        db.query(func.count(User.id)).filter(User.role == UserRole.CUSTOMER, User.is_active.is_(True)).scalar() or 0
    )
    pending_kyc = (
        db.query(func.count(CustomerProfile.id))
        .filter(CustomerProfile.kyc_status == KycStatus.PENDING)
        .scalar()
        or 0
    )
    pending_transfers = (
        db.query(func.count(Transfer.id))
        .filter(
            Transfer.status.in_([
                TransferStatus.COMPLIANCE_REVIEW,
                TransferStatus.READY_FOR_PROCESSING,
                TransferStatus.AWAITING_PAYMENT,
                TransferStatus.PAYMENT_PENDING_VERIFICATION,
            ])
        )
        .scalar()
        or 0
    )
    completed = (
        db.query(func.count(Transfer.id)).filter(Transfer.status == TransferStatus.COMPLETED).scalar() or 0
    )
    failed = db.query(func.count(Transfer.id)).filter(Transfer.status == TransferStatus.FAILED).scalar() or 0
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
    waitlist_count = db.query(func.count(WaitlistLead.id)).scalar() or 0

    return {
        "total_customers": total_customers,
        "pending_kyc": pending_kyc,
        "pending_transfers": pending_transfers,
        "completed_transfers": completed,
        "failed_transfers": failed,
        "daily_volume_zar": str(Decimal(str(daily_volume))),
        "monthly_volume_zar": str(Decimal(str(monthly_volume))),
        "waitlist_leads": waitlist_count,
    }
