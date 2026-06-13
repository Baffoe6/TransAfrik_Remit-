"""Phase 12 — Security Center admin API."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.models.enums import SecurityEventType, UserRole
from app.models.security import SecurityAuditLog, UserSession
from app.models.security_hardening import AdminIpAllowlist, SecurityAlert
from app.models.user import User
from app.secrets.provider import check_production_secrets
from app.services.account_security_service import STAFF_ROLES
from app.services.anomaly_detection_service import (
    get_failed_logins,
    get_risk_events,
)
from app.services.ip_allowlist_service import add_allowlist_entry, list_allowlist
from app.services.security_service import (
    get_staff_mfa_summary,
    list_active_sessions,
    log_security_event,
    revoke_all_sessions,
    revoke_session_by_id,
)

router = APIRouter(prefix="/admin/security-center", tags=["Security Center"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]
settings = get_settings()


class IpAllowlistCreate(BaseModel):
    ip_cidr: str = Field(min_length=3, max_length=64)
    label: str | None = None
    user_id: int | None = None


class AlertResolve(BaseModel):
    resolved: bool = True


@router.get("/dashboard")
def security_dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    since_24h = datetime.now(UTC) - timedelta(hours=24)
    failed_24h = (
        db.query(func.count(SecurityAuditLog.id))
        .filter(
            SecurityAuditLog.event_type == SecurityEventType.LOGIN_FAILED,
            SecurityAuditLog.created_at >= since_24h,
        )
        .scalar()
        or 0
    )
    active_sessions = (
        db.query(func.count(UserSession.id))
        .filter(UserSession.is_revoked.is_(False), UserSession.expires_at > datetime.now(UTC))
        .scalar()
        or 0
    )
    staff_total = db.query(func.count(User.id)).filter(User.role.in_(STAFF_ROLES)).scalar() or 0
    mfa_summary = get_staff_mfa_summary(db)
    mfa_enabled_count = sum(1 for s in mfa_summary if s["mfa_enabled"])
    unresolved_alerts = (
        db.query(func.count(SecurityAlert.id))
        .filter(SecurityAlert.is_resolved.is_(False))
        .scalar()
        or 0
    )
    locked_accounts = (
        db.query(func.count(User.id))
        .filter(User.locked_until.isnot(None), User.locked_until > datetime.now(UTC))
        .scalar()
        or 0
    )
    return {
        "summary": {
            "failed_logins_24h": failed_24h,
            "active_sessions": active_sessions,
            "staff_mfa_enabled": mfa_enabled_count,
            "staff_total": staff_total,
            "unresolved_alerts": unresolved_alerts,
            "locked_accounts": locked_accounts,
            "admin_mfa_required": settings.admin_mfa_required,
            "ip_allowlist_enabled": settings.admin_ip_allowlist_enabled,
            "lockout_max_attempts": settings.account_lockout_max_attempts,
            "password_max_age_days": settings.password_max_age_days,
        },
        "secrets_checklist": check_production_secrets(),
    }


@router.get("/failed-logins")
def failed_logins(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 50):
    rows = get_failed_logins(db, limit)
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "ip_address": r.ip_address,
            "details": r.details,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/sessions")
def active_sessions(admin: AdminUser, db: Annotated[Session, Depends(get_db)], user_id: int | None = None):
    sessions = list_active_sessions(db, user_id=user_id)
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "created_at": s.created_at.isoformat(),
            "last_used_at": s.last_used_at.isoformat() if s.last_used_at else None,
            "expires_at": s.expires_at.isoformat(),
        }
        for s in sessions
    ]


@router.post("/sessions/{session_id}/revoke")
def revoke_session(
    session_id: int,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not revoke_session_by_id(db, session_id):
        raise HTTPException(status_code=400, detail="Session already revoked")
    log_security_event(
        db,
        event_type=SecurityEventType.SESSION_REVOKED,
        user_id=session.user_id,
        ip_address=get_client_ip(request),
        details=f"revoked_by_admin={admin.id} session_id={session_id}",
    )
    db.commit()
    return {"message": "Session revoked", "session_id": session_id}


@router.post("/sessions/revoke-all")
def revoke_user_sessions(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    user_id: int = Query(...),
):
    count = revoke_all_sessions(db, user_id)
    log_security_event(
        db,
        event_type=SecurityEventType.SESSION_REVOKED,
        user_id=user_id,
        ip_address=get_client_ip(request),
        details=f"revoked_all_by_admin={admin.id} count={count}",
    )
    db.commit()
    return {"revoked": count}


@router.get("/mfa-status")
def mfa_status(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return {
        "admin_mfa_required": settings.admin_mfa_required,
        "staff": get_staff_mfa_summary(db),
    }


@router.get("/alerts")
def security_alerts(admin: AdminUser, db: Annotated[Session, Depends(get_db)], resolved: bool | None = False):
    query = db.query(SecurityAlert).order_by(SecurityAlert.created_at.desc()).limit(100)
    if resolved is not None:
        query = query.filter(SecurityAlert.is_resolved.is_(resolved))
    alerts = query.all()
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "user_id": a.user_id,
            "ip_address": a.ip_address,
            "title": a.title,
            "details": a.details,
            "is_resolved": a.is_resolved,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.patch("/alerts/{alert_id}")
def resolve_alert(alert_id: int, data: AlertResolve, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = data.resolved
    db.commit()
    return {"id": alert.id, "is_resolved": alert.is_resolved}


@router.get("/risk-events")
def risk_events(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 50):
    rows = get_risk_events(db, limit)
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "event_type": r.event_type.value,
            "ip_address": r.ip_address,
            "details": r.details,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/audit-trail")
def audit_trail(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 100, event_type: str | None = None):
    query = db.query(SecurityAuditLog).order_by(SecurityAuditLog.created_at.desc())
    if event_type:
        try:
            query = query.filter(SecurityAuditLog.event_type == SecurityEventType(event_type))
        except ValueError:
            pass
    logs = query.limit(limit).all()
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "event_type": l.event_type.value,
            "ip_address": l.ip_address,
            "user_agent": l.user_agent,
            "details": l.details,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]


@router.get("/ip-allowlist")
def get_ip_allowlist(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    entries = list_allowlist(db)
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "ip_cidr": e.ip_cidr,
            "label": e.label,
            "is_active": e.is_active,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]


@router.post("/ip-allowlist", status_code=status.HTTP_201_CREATED)
def create_ip_allowlist(
    data: IpAllowlistCreate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
):
    entry = add_allowlist_entry(
        db,
        ip_cidr=data.ip_cidr,
        label=data.label,
        user_id=data.user_id,
        created_by=admin.id,
    )
    db.commit()
    return {"id": entry.id, "ip_cidr": entry.ip_cidr}


@router.delete("/ip-allowlist/{entry_id}")
def delete_ip_allowlist(entry_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    entry = db.query(AdminIpAllowlist).filter(AdminIpAllowlist.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Allowlist entry not found")
    entry.is_active = False
    db.commit()
    return {"message": "Allowlist entry deactivated"}
