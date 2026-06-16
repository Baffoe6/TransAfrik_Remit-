"""Keep user verification flags aligned with KYC outcomes."""

from sqlalchemy.orm import Session

from app.models.customer_profile import CustomerProfile
from app.models.enums import KycStatus
from app.models.user import User


def sync_identity_verification(db: Session, user: User) -> bool:
    """Approved KYC implies the mobile identity was verified by compliance."""
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user.id).first()
    if not profile or profile.kyc_status != KycStatus.APPROVED:
        return False
    if user.phone_verified:
        return False
    user.phone_verified = True
    db.commit()
    db.refresh(user)
    return True
