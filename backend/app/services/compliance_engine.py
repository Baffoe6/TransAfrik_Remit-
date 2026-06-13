from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.compliance import CustomerRiskProfile, EnhancedDueDiligenceCase, SanctionsScreening
from app.models.customer_profile import CustomerProfile
from app.models.enums import EddStatus, SanctionsResult, TransferStatus
from app.models.transfer import Transfer
from app.services.aml import calculate_risk_score, evaluate_aml_flags


def _risk_level(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def screen_sanctions(db: Session, *, name: str, user_id: int | None, transfer_id: int | None) -> SanctionsScreening:
    """Placeholder sanctions screening — replace with OFAC/UN list API integration."""
    blocked_tokens = {"test_sanction", "blocked_name"}
    normalized = name.lower()
    result = SanctionsResult.CLEAR
    match_details = None

    for token in blocked_tokens:
        if token in normalized:
            result = SanctionsResult.POTENTIAL_MATCH
            match_details = {"matched_token": token, "provider": "internal_placeholder"}
            break

    screening = SanctionsScreening(
        user_id=user_id,
        transfer_id=transfer_id,
        screened_name=name,
        result=result,
        match_details=match_details,
        provider="internal_placeholder",
    )
    db.add(screening)
    db.flush()
    return screening


def update_customer_risk_profile(db: Session, user_id: int) -> CustomerRiskProfile:
    profile = db.query(CustomerRiskProfile).filter(CustomerRiskProfile.user_id == user_id).first()
    if not profile:
        profile = CustomerRiskProfile(user_id=user_id)
        db.add(profile)

    transfers = db.query(Transfer).filter(Transfer.user_id == user_id).all()
    total_volume = sum((t.send_amount_zar for t in transfers), Decimal("0"))
    aml_count = sum(1 for t in transfers if t.aml_flags)

    latest_scores = [t.risk_score for t in transfers if t.risk_score]
    avg_score = sum(latest_scores) // len(latest_scores) if latest_scores else 0

    profile.transfer_count = len(transfers)
    profile.total_transfer_volume_zar = total_volume
    profile.aml_flag_count = aml_count
    profile.risk_score = min(100, avg_score + aml_count * 5)
    profile.risk_level = _risk_level(profile.risk_score)
    profile.updated_at = datetime.now(UTC)
    db.flush()
    return profile


def open_edd_case(
    db: Session,
    *,
    user_id: int,
    transfer_id: int | None,
    reason: str,
    risk_score: int,
    aml_flags: list | dict | None,
) -> EnhancedDueDiligenceCase:
    case = EnhancedDueDiligenceCase(
        user_id=user_id,
        transfer_id=transfer_id,
        reason=reason,
        risk_score=risk_score,
        aml_flags=aml_flags,
        status=EddStatus.OPEN,
    )
    db.add(case)
    db.flush()
    return case


def run_transfer_compliance(
    db: Session,
    *,
    user_id: int,
    send_amount_zar: Decimal,
    beneficiary: Beneficiary,
    profile: CustomerProfile,
    transfer_id: int | None = None,
) -> dict:
    aml_flags = evaluate_aml_flags(
        db, user_id=user_id, send_amount_zar=send_amount_zar, beneficiary=beneficiary, profile=profile
    )

    sender_name = f"{profile.first_name} {profile.last_name}"
    sender_screen = screen_sanctions(db, name=sender_name, user_id=user_id, transfer_id=transfer_id)
    beneficiary_screen = screen_sanctions(db, name=beneficiary.full_name, user_id=user_id, transfer_id=transfer_id)

    if sender_screen.result != SanctionsResult.CLEAR:
        aml_flags.append({"type": "sanctions_hit", "message": f"Sanctions screening flag on sender: {sender_name}"})
    if beneficiary_screen.result != SanctionsResult.CLEAR:
        aml_flags.append({"type": "sanctions_hit", "message": f"Sanctions screening flag on beneficiary: {beneficiary.full_name}"})

    risk_score = calculate_risk_score(aml_flags)
    update_customer_risk_profile(db, user_id)

    edd_case = None
    if risk_score >= 40 or aml_flags:
        edd_case = open_edd_case(
            db,
            user_id=user_id,
            transfer_id=transfer_id,
            reason="Automated compliance review triggered",
            risk_score=risk_score,
            aml_flags=aml_flags,
        )

    return {"aml_flags": aml_flags, "risk_score": risk_score, "edd_case_id": edd_case.id if edd_case else None}
