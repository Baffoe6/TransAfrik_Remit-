from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.enums import AmlFlagType, TransferStatus
from app.models.transfer import Transfer

HIGH_VALUE_THRESHOLD_ZAR = Decimal("10000")
REPEATED_TRANSFER_WINDOW_DAYS = 7
REPEATED_TRANSFER_COUNT = 3
MULTIPLE_BENEFICIARY_THRESHOLD = 5
SHARED_BENEFICIARY_THRESHOLD = 2


def _normalize_name(name: str) -> set[str]:
    return {part.lower() for part in name.split() if len(part) > 1}


def check_name_mismatch(sender_profile: CustomerProfile, beneficiary: Beneficiary) -> bool:
    sender_name = f"{sender_profile.first_name} {sender_profile.last_name}"
    sender_parts = _normalize_name(sender_name)
    beneficiary_parts = _normalize_name(beneficiary.full_name)
    if not sender_parts or not beneficiary_parts:
        return False
    return len(sender_parts & beneficiary_parts) == 0


def check_shared_beneficiary(db: Session, beneficiary: Beneficiary, exclude_user_id: int) -> bool:
    other_senders = (
        db.query(func.count(func.distinct(Transfer.user_id)))
        .join(Beneficiary, Transfer.beneficiary_id == Beneficiary.id)
        .filter(
            Beneficiary.mobile_wallet_number == beneficiary.mobile_wallet_number,
            Transfer.user_id != exclude_user_id,
            Transfer.status.notin_([TransferStatus.FAILED, TransferStatus.REFUNDED, TransferStatus.EXPIRED]),
        )
        .scalar()
        or 0
    )
    return other_senders >= SHARED_BENEFICIARY_THRESHOLD


def calculate_risk_score(flags: list[dict]) -> int:
    weights = {
        AmlFlagType.HIGH_VALUE.value: 30,
        AmlFlagType.REPEATED_TRANSFERS.value: 25,
        AmlFlagType.MULTIPLE_BENEFICIARIES.value: 15,
        AmlFlagType.NAME_MISMATCH.value: 20,
        AmlFlagType.SHARED_BENEFICIARY.value: 35,
    }
    return min(100, sum(weights.get(f["type"], 10) for f in flags))


def evaluate_aml_flags(
    db: Session,
    *,
    user_id: int,
    send_amount_zar: Decimal,
    beneficiary: Beneficiary,
    profile: CustomerProfile,
) -> list[dict]:
    flags: list[dict] = []

    if send_amount_zar >= HIGH_VALUE_THRESHOLD_ZAR:
        flags.append({
            "type": AmlFlagType.HIGH_VALUE.value,
            "message": f"Transfer amount R{send_amount_zar} exceeds high-value threshold R{HIGH_VALUE_THRESHOLD_ZAR}",
        })

    window_start = datetime.now(UTC) - timedelta(days=REPEATED_TRANSFER_WINDOW_DAYS)
    recent_count = (
        db.query(func.count(Transfer.id))
        .filter(
            Transfer.user_id == user_id,
            Transfer.created_at >= window_start,
            Transfer.status.notin_([TransferStatus.FAILED, TransferStatus.REFUNDED, TransferStatus.EXPIRED]),
        )
        .scalar()
        or 0
    )
    if recent_count >= REPEATED_TRANSFER_COUNT:
        flags.append({
            "type": AmlFlagType.REPEATED_TRANSFERS.value,
            "message": f"Customer has {recent_count + 1} transfers in the last {REPEATED_TRANSFER_WINDOW_DAYS} days",
        })

    beneficiary_count = (
        db.query(func.count(Beneficiary.id))
        .filter(Beneficiary.user_id == user_id, Beneficiary.is_active.is_(True))
        .scalar()
        or 0
    )
    if beneficiary_count >= MULTIPLE_BENEFICIARY_THRESHOLD:
        flags.append({
            "type": AmlFlagType.MULTIPLE_BENEFICIARIES.value,
            "message": f"Customer has {beneficiary_count} active beneficiaries",
        })

    if check_name_mismatch(profile, beneficiary):
        flags.append({
            "type": AmlFlagType.NAME_MISMATCH.value,
            "message": "Sender and beneficiary names do not appear to match",
        })

    if check_shared_beneficiary(db, beneficiary, user_id):
        flags.append({
            "type": AmlFlagType.SHARED_BENEFICIARY.value,
            "message": "Beneficiary wallet receives from multiple senders",
        })

    return flags
