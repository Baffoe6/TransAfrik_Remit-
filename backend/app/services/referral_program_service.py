import secrets
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import OperationsAuditCategory, ReferralRewardType, VoucherStatus
from app.models.referral_program import (
    CustomerReferral,
    DiscountVoucher,
    ReferralProgram,
    ReferralReward,
)
from app.models.user import User
from app.services.operations_audit import log_operations_action


def get_active_program(db: Session) -> ReferralProgram | None:
    return db.query(ReferralProgram).filter(ReferralProgram.is_active.is_(True)).first()


def ensure_program(db: Session) -> ReferralProgram:
    program = get_active_program(db)
    if program:
        return program
    program = ReferralProgram(name="TransAfrik Customer Referrals")
    db.add(program)
    db.flush()
    return program


def generate_referral_code(db: Session, user_id: int) -> str:
    for _ in range(10):
        code = f"REF{secrets.token_hex(3).upper()}"
        exists = db.query(CustomerReferral).filter(CustomerReferral.referral_code == code).first()
        if not exists:
            return code
    return f"REF{user_id:06d}"


def get_or_create_user_referral_code(db: Session, user_id: int) -> str:
    program = ensure_program(db)
    existing = (
        db.query(CustomerReferral)
        .filter(CustomerReferral.referrer_user_id == user_id, CustomerReferral.referred_user_id.is_(None))
        .first()
    )
    if existing:
        return existing.referral_code
    code = generate_referral_code(db, user_id)
    ref = CustomerReferral(program_id=program.id, referrer_user_id=user_id, referral_code=code)
    db.add(ref)
    db.flush()
    return code


def record_referral_signup(db: Session, referral_code: str, new_user_id: int) -> CustomerReferral | None:
    program = get_active_program(db)
    if not program:
        return None
    template = (
        db.query(CustomerReferral)
        .filter(CustomerReferral.referral_code == referral_code.upper())
        .first()
    )
    if not template or template.referrer_user_id == new_user_id:
        return None

    referral = CustomerReferral(
        program_id=program.id,
        referrer_user_id=template.referrer_user_id,
        referred_user_id=new_user_id,
        referral_code=referral_code.upper(),
        converted=True,
    )
    db.add(referral)
    db.flush()

    reward = ReferralReward(
        user_id=template.referrer_user_id,
        reward_type=ReferralRewardType.REFERRAL_SIGNUP,
        points=program.points_per_referral,
        description=f"Referral signup: user {new_user_id}",
        referral_id=referral.id,
    )
    db.add(reward)
    _maybe_issue_voucher(db, template.referrer_user_id, program)
    log_operations_action(
        db,
        category=OperationsAuditCategory.REFERRAL,
        action="referral_signup_recorded",
        entity_type="customer_referral",
        entity_id=referral.id,
        user_id=new_user_id,
        details={"referrer": template.referrer_user_id, "code": referral_code},
    )
    return referral


def _maybe_issue_voucher(db: Session, user_id: int, program: ReferralProgram) -> DiscountVoucher | None:
    total_points = (
        db.query(func.coalesce(func.sum(ReferralReward.points), 0))
        .filter(ReferralReward.user_id == user_id)
        .scalar()
    ) or 0
    if int(total_points) < program.voucher_threshold_points:
        return None
    if int(total_points) % program.voucher_threshold_points != 0:
        return None

    code = f"VOUCH{secrets.token_hex(4).upper()}"
    voucher = DiscountVoucher(
        user_id=user_id,
        code=code,
        discount_zar=program.voucher_discount_zar,
        status=VoucherStatus.ACTIVE,
    )
    db.add(voucher)
    db.flush()
    return voucher


def get_customer_referral_dashboard(db: Session, user_id: int) -> dict:
    program = ensure_program(db)
    code = get_or_create_user_referral_code(db, user_id)
    referrals = (
        db.query(CustomerReferral)
        .filter(CustomerReferral.referrer_user_id == user_id, CustomerReferral.referred_user_id.isnot(None))
        .order_by(CustomerReferral.created_at.desc())
        .limit(50)
        .all()
    )
    total_points = (
        db.query(func.coalesce(func.sum(ReferralReward.points), 0))
        .filter(ReferralReward.user_id == user_id)
        .scalar()
    ) or 0
    vouchers = (
        db.query(DiscountVoucher)
        .filter(DiscountVoucher.user_id == user_id)
        .order_by(DiscountVoucher.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "referral_code": code,
        "program_name": program.name,
        "total_points": int(total_points),
        "voucher_threshold": program.voucher_threshold_points,
        "referrals_made": len(referrals),
        "referrals": [
            {
                "id": r.id,
                "referred_user_id": r.referred_user_id,
                "converted": r.converted,
                "created_at": r.created_at.isoformat(),
            }
            for r in referrals
        ],
        "vouchers": [
            {
                "code": v.code,
                "discount_zar": str(v.discount_zar),
                "status": v.status.value if hasattr(v.status, "value") else v.status,
                "expires_at": v.expires_at.isoformat() if v.expires_at else None,
            }
            for v in vouchers
        ],
    }


def get_founder_referral_metrics(db: Session) -> dict:
    total_referrals = db.query(func.count(CustomerReferral.id)).filter(
        CustomerReferral.referred_user_id.isnot(None)
    ).scalar() or 0
    converted = db.query(func.count(CustomerReferral.id)).filter(CustomerReferral.converted.is_(True)).scalar() or 0
    total_customers = db.query(func.count(User.id)).scalar() or 1
    conversion_rate = round((converted / max(total_customers, 1)) * 100, 2)

    top_referrers = (
        db.query(
            CustomerReferral.referrer_user_id,
            func.count(CustomerReferral.id).label("count"),
        )
        .filter(CustomerReferral.referred_user_id.isnot(None))
        .group_by(CustomerReferral.referrer_user_id)
        .order_by(func.count(CustomerReferral.id).desc())
        .limit(10)
        .all()
    )

    return {
        "total_referrals": total_referrals,
        "converted_referrals": converted,
        "conversion_rate_percent": conversion_rate,
        "top_referrers": [{"user_id": uid, "referrals": cnt} for uid, cnt in top_referrers],
    }
