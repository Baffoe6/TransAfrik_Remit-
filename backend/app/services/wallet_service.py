import secrets
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import OperationsAuditCategory, TransferStatus
from app.models.transfer import Transfer
from app.models.wallet_profile import CustomerWalletProfile


def get_or_create_wallet_profile(db: Session, user_id: int) -> CustomerWalletProfile:
    profile = db.query(CustomerWalletProfile).filter(CustomerWalletProfile.user_id == user_id).first()
    if not profile:
        profile = CustomerWalletProfile(
            user_id=user_id,
            referral_code=f"TA{secrets.token_hex(4).upper()}",
        )
        db.add(profile)
        db.flush()
    return profile


def refresh_wallet_stats(db: Session, user_id: int) -> CustomerWalletProfile:
    profile = get_or_create_wallet_profile(db, user_id)
    transfers = db.query(Transfer).filter(Transfer.user_id == user_id).all()
    completed = [t for t in transfers if t.status == TransferStatus.COMPLETED]

    profile.transfer_count = len(transfers)
    profile.completed_transfer_count = len(completed)
    profile.total_sent_zar = sum((t.send_amount_zar for t in completed), Decimal("0"))
    profile.total_fees_zar = sum((t.fee_zar for t in completed), Decimal("0"))

    last = db.query(func.max(Transfer.created_at)).filter(Transfer.user_id == user_id).scalar()
    profile.last_transfer_at = last
    profile.updated_at = datetime.now(UTC)
    db.flush()
    return profile


def wallet_profile_response(profile: CustomerWalletProfile) -> dict:
    return {
        "user_id": profile.user_id,
        "total_sent_zar": str(profile.total_sent_zar),
        "total_fees_zar": str(profile.total_fees_zar),
        "transfer_count": profile.transfer_count,
        "completed_transfer_count": profile.completed_transfer_count,
        "preferred_corridor": profile.preferred_corridor,
        "referral_code": profile.referral_code,
        "last_transfer_at": profile.last_transfer_at.isoformat() if profile.last_transfer_at else None,
        "disclaimer": "This profile shows transfer activity only. TransAfrik does not hold stored funds.",
    }
