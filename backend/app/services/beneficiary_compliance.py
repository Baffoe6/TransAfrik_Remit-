"""Beneficiary-level compliance screening — auto-approve unless flags are raised."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.enums import AmlFlagType, BeneficiaryStatus, SanctionsResult
from app.models.user import User
from app.services.aml import (
    MULTIPLE_BENEFICIARY_THRESHOLD,
    check_name_mismatch,
    check_shared_beneficiary,
)
from app.services.compliance_engine import screen_sanctions


def evaluate_beneficiary_compliance(
    db: Session,
    *,
    user: User,
    beneficiary: Beneficiary,
    profile: CustomerProfile | None,
) -> list[dict]:
    flags: list[dict] = []

    if profile and check_name_mismatch(profile, beneficiary):
        flags.append({
            "type": AmlFlagType.NAME_MISMATCH.value,
            "message": "Sender and beneficiary names do not appear to match",
        })

    if beneficiary.mobile_wallet_number and check_shared_beneficiary(db, beneficiary, user.id):
        flags.append({
            "type": AmlFlagType.SHARED_BENEFICIARY.value,
            "message": "Beneficiary wallet receives from multiple senders",
        })

    beneficiary_count = (
        db.query(func.count(Beneficiary.id))
        .filter(Beneficiary.user_id == user.id, Beneficiary.is_active.is_(True))
        .scalar()
        or 0
    )
    if beneficiary_count >= MULTIPLE_BENEFICIARY_THRESHOLD:
        flags.append({
            "type": AmlFlagType.MULTIPLE_BENEFICIARIES.value,
            "message": f"Customer has {beneficiary_count} active beneficiaries",
        })

    screening = screen_sanctions(
        db,
        name=beneficiary.full_name,
        user_id=user.id,
        transfer_id=None,
    )
    if screening.result != SanctionsResult.CLEAR:
        flags.append({
            "type": AmlFlagType.SANCTIONS_HIT.value,
            "message": "Beneficiary name requires compliance review",
        })

    return flags


def resolve_beneficiary_status(flags: list[dict]) -> BeneficiaryStatus:
    """Recipients are customer-managed and usable for sends immediately.

    Compliance flags are retained for admin review but do not block sending.
    """
    _ = flags
    return BeneficiaryStatus.APPROVED
