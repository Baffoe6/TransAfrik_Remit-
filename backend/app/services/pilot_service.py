"""Pilot launch mode: invites, approval workflow, transfer limits."""

import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.corridor import Corridor
from app.models.enums import OperationsAuditCategory, PilotCustomerStatus, PilotInviteStatus, TransferStatus
from app.models.pilot import PilotCustomer, PilotInvite, PilotSettings
from app.models.transfer import Transfer
from app.services.operations_audit import log_operations_action


def get_pilot_settings(db: Session) -> PilotSettings:
    settings = db.query(PilotSettings).first()
    if not settings:
        settings = PilotSettings(
            pilot_mode_enabled=False,
            invite_only_registration=True,
            require_admin_approval=True,
            default_allowed_corridors=["ZA-GH"],
        )
        db.add(settings)
        db.flush()
    return settings


def create_invite(
    db: Session,
    *,
    email: str | None,
    max_uses: int,
    expires_days: int | None,
    created_by: int,
) -> PilotInvite:
    code = f"PILOT{secrets.token_hex(4).upper()}"
    invite = PilotInvite(
        invite_code=code,
        email=email.lower() if email else None,
        max_uses=max_uses,
        expires_at=datetime.now(UTC) + timedelta(days=expires_days) if expires_days else None,
        created_by=created_by,
    )
    db.add(invite)
    log_operations_action(
        db,
        category=OperationsAuditCategory.PILOT,
        action="pilot_invite_created",
        entity_type="pilot_invite",
        user_id=created_by,
        details={"code": code, "email": email},
    )
    return invite


def validate_invite_for_registration(
    db: Session, email: str | None, mobile_number: str, invite_code: str | None
) -> PilotInvite | None:
    settings = get_pilot_settings(db)
    if not settings.pilot_mode_enabled or not settings.invite_only_registration:
        return None
    if not invite_code:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pilot invite code required")
    invite = db.query(PilotInvite).filter(PilotInvite.invite_code == invite_code.upper()).first()
    if not invite or invite.status != PilotInviteStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired invite code")
    if invite.expires_at and invite.expires_at < datetime.now(UTC):
        invite.status = PilotInviteStatus.EXPIRED
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invite code has expired")
    if invite.uses_count >= invite.max_uses:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invite code already used")
    if invite.email and email and invite.email.lower() != email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invite code not valid for this email")
    if invite.email and not email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This invite requires an email address")
    return invite


def register_pilot_customer(db: Session, user_id: int, invite: PilotInvite | None) -> PilotCustomer | None:
    settings = get_pilot_settings(db)
    if not settings.pilot_mode_enabled:
        return None
    status_val = PilotCustomerStatus.PENDING if settings.require_admin_approval else PilotCustomerStatus.APPROVED
    pilot = PilotCustomer(
        user_id=user_id,
        status=status_val,
        invite_code_used=invite.invite_code if invite else None,
        max_transfer_zar=settings.default_max_transfer_zar,
        daily_transfer_limit=settings.default_daily_transfer_limit,
        monthly_volume_zar=settings.default_monthly_volume_zar,
        allowed_corridors=settings.default_allowed_corridors,
    )
    db.add(pilot)
    if invite:
        invite.uses_count += 1
    db.flush()
    return pilot


def approve_pilot_customer(db: Session, pilot: PilotCustomer, admin_id: int, notes: str | None = None) -> PilotCustomer:
    pilot.status = PilotCustomerStatus.APPROVED
    pilot.approved_by = admin_id
    pilot.approved_at = datetime.now(UTC)
    if notes:
        pilot.admin_notes = notes
    log_operations_action(
        db,
        category=OperationsAuditCategory.PILOT,
        action="pilot_customer_approved",
        entity_type="pilot_customer",
        entity_id=pilot.id,
        user_id=admin_id,
    )
    return pilot


def get_pilot_customer(db: Session, user_id: int) -> PilotCustomer | None:
    return db.query(PilotCustomer).filter(PilotCustomer.user_id == user_id).first()


def check_transfer_limits(db: Session, user_id: int, send_amount: Decimal, beneficiary: Beneficiary) -> None:
    settings = get_pilot_settings(db)
    if not settings.pilot_mode_enabled:
        return
    pilot = get_pilot_customer(db, user_id)
    if not pilot:
        return
    if pilot.status != PilotCustomerStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pilot account pending approval")

    max_transfer = pilot.max_transfer_zar or settings.default_max_transfer_zar
    if send_amount > max_transfer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Transfer exceeds pilot limit of R{max_transfer}",
        )

    daily_limit = pilot.daily_transfer_limit or settings.default_daily_transfer_limit
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_count = (
        db.query(func.count(Transfer.id))
        .filter(Transfer.user_id == user_id, Transfer.created_at >= today_start)
        .scalar()
        or 0
    )
    if daily_count >= daily_limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Daily transfer limit reached")

    monthly_cap = pilot.monthly_volume_zar or settings.default_monthly_volume_zar
    month_start = today_start.replace(day=1)
    monthly_volume = (
        db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0))
        .filter(Transfer.user_id == user_id, Transfer.created_at >= month_start)
        .scalar()
    ) or Decimal("0")
    if monthly_volume + send_amount > monthly_cap:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Monthly volume limit reached")

    allowed = pilot.allowed_corridors or settings.default_allowed_corridors or []
    if allowed:
        corridor_code = f"ZA-{beneficiary.country}"
        if corridor_code not in allowed:
            active = (
                db.query(Corridor)
                .filter(Corridor.destination_country == beneficiary.country, Corridor.code.in_(allowed))
                .first()
            )
            if not active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Corridor ZA→{beneficiary.country} not enabled for pilot account",
                )


def get_pilot_dashboard(db: Session, user_id: int) -> dict:
    settings = get_pilot_settings(db)
    pilot = get_pilot_customer(db, user_id)
    from app.models.customer_profile import CustomerProfile
    from app.models.kyc_document import KycDocument

    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()
    kyc_docs = db.query(KycDocument).filter(KycDocument.user_id == user_id).count()
    transfers = db.query(Transfer).filter(Transfer.user_id == user_id).count()
    completed = (
        db.query(Transfer)
        .filter(Transfer.user_id == user_id, Transfer.status == TransferStatus.COMPLETED)
        .count()
    )

    checklist = [
        {"step": "Account approved", "done": pilot.status == PilotCustomerStatus.APPROVED if pilot else True},
        {"step": "KYC submitted", "done": kyc_docs > 0},
        {"step": "KYC approved", "done": (profile.kyc_status.value if hasattr(profile.kyc_status, "value") else profile.kyc_status) == "approved" if profile else False},
        {"step": "Beneficiary added", "done": db.query(Beneficiary).filter(Beneficiary.user_id == user_id).count() > 0},
        {"step": "First transfer completed", "done": completed > 0},
    ]

    return {
        "pilot_mode_active": settings.pilot_mode_enabled,
        "status": pilot.status.value if pilot else "approved",
        "limits": {
            "max_transfer_zar": str(pilot.max_transfer_zar or settings.default_max_transfer_zar) if pilot else None,
            "daily_transfer_limit": pilot.daily_transfer_limit or settings.default_daily_transfer_limit if pilot else None,
            "monthly_volume_zar": str(pilot.monthly_volume_zar or settings.default_monthly_volume_zar) if pilot else None,
            "allowed_corridors": pilot.allowed_corridors or settings.default_allowed_corridors if pilot else [],
        },
        "kyc_status": profile.kyc_status.value if profile else "not_submitted",
        "transfer_count": transfers,
        "first_transfer_checklist": checklist,
        "support_contact": {"email": "support@transafrik.co.za", "whatsapp": "+27 support line"},
        "demo_warning": settings.demo_mode_enabled,
    }
