"""Customer dashboard aggregation service."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.enums import KycStatus, TransferStatus
from app.models.kyc_document import KycDocument
from app.models.referral_program import CustomerReferral
from app.models.transfer import Transfer
from app.services.transfer_status_mapper import to_mvp_status


def _kyc_display_status(status: KycStatus | str) -> str:
    mapping = {
        KycStatus.NOT_SUBMITTED: "Draft",
        KycStatus.PENDING: "Submitted",
        KycStatus.APPROVED: "Approved",
        KycStatus.REJECTED: "Rejected",
    }
    if isinstance(status, str):
        try:
            status = KycStatus(status)
        except ValueError:
            return status.title()
    return mapping.get(status, status.value.title())


def _profile_completion(profile: CustomerProfile | None) -> dict:
    if not profile:
        return {"percent": 0, "missing": ["profile"]}
    fields = {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "phone": True,
        "date_of_birth": profile.date_of_birth,
        "id_number": profile.id_number,
        "address": profile.address_line1,
    }
    filled = sum(1 for v in fields.values() if v)
    missing = [k for k, v in fields.items() if not v]
    return {"percent": int((filled / len(fields)) * 100), "missing": missing}


def get_customer_dashboard(db: Session, user_id: int) -> dict:
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()
    docs = db.query(KycDocument).filter(KycDocument.user_id == user_id).all()
    beneficiaries = (
        db.query(Beneficiary)
        .filter(Beneficiary.user_id == user_id, Beneficiary.is_active.is_(True))
        .order_by(Beneficiary.created_at.desc())
        .all()
    )
    transfers = (
        db.query(Transfer)
        .filter(Transfer.user_id == user_id)
        .order_by(Transfer.created_at.desc())
        .limit(50)
        .all()
    )
    referral = db.query(CustomerReferral).filter(CustomerReferral.referrer_user_id == user_id).count()

    return {
        "profile_completion": _profile_completion(profile),
        "kyc": {
            "status": _kyc_display_status(profile.kyc_status) if profile else "Draft",
            "raw_status": profile.kyc_status.value if profile else "not_submitted",
            "documents_uploaded": len(docs),
            "rejection_reason": profile.kyc_rejection_reason if profile else None,
        },
        "beneficiaries": {
            "count": len(beneficiaries),
            "items": [
                {
                    "id": b.id,
                    "full_name": b.full_name,
                    "country": b.country,
                    "mobile_wallet_number": b.mobile_wallet_number,
                    "mobile_money_provider": b.mobile_money_provider,
                    "relationship_to_sender": b.relationship_to_sender,
                    "status": b.status.value if hasattr(b.status, "value") else b.status,
                }
                for b in beneficiaries[:10]
            ],
        },
        "transfers": {
            "count": len(transfers),
            "recent": [
                {
                    "id": t.id,
                    "reference": t.reference,
                    "status": to_mvp_status(t.status),
                    "send_amount_zar": str(t.send_amount_zar),
                    "receive_amount_ghs": str(t.receive_amount_ghs),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in transfers[:5]
            ],
        },
        "transaction_history": [
            {
                "id": t.id,
                "reference": t.reference,
                "status": to_mvp_status(t.status),
                "send_amount_zar": str(t.send_amount_zar),
                "receive_amount_ghs": str(t.receive_amount_ghs),
                "fee_zar": str(t.fee_zar),
                "exchange_rate": str(t.exchange_rate),
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in transfers
        ],
        "referral_program": {"referrals_made": referral},
    }
