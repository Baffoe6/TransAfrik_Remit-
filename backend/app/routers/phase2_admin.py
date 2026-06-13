"""Phase 2 admin routes: exchange rates, fees, compliance EDD, providers, notifications, security."""

from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.models.compliance import EnhancedDueDiligenceCase
from app.models.enums import EddStatus, UserRole
from app.models.fee_rule import FeeRule
from app.models.notification import NotificationLog, NotificationTemplate
from app.models.security import SecurityAuditLog, UserMfa, UserSession
from app.models.user import User
from app.models.webhook import ProviderConfig
from app.services.exchange_rate_engine import create_exchange_rate, list_rate_history
from app.services.security_service import enable_mfa, log_security_event, revoke_all_sessions, setup_mfa, verify_mfa_code
from app.models.enums import SecurityEventType

router = APIRouter(prefix="/admin", tags=["Admin Phase 2"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER))]


class ExchangeRateCreateV2(BaseModel):
    from_currency: str = "ZAR"
    to_currency: str = "GHS"
    rate: Decimal = Field(gt=0, decimal_places=6)
    effective_from: date
    effective_to: date | None = None
    change_reason: str | None = None


class FeeRuleCreateV2(BaseModel):
    name: str
    min_amount_zar: Decimal = Field(ge=0)
    max_amount_zar: Decimal | None = None
    fee_type: str = "flat"
    fee_value: Decimal = Field(gt=0)
    destination_country: str | None = None
    payment_method_id: int | None = None
    provider_id: int | None = None
    priority: int = 0


class ProviderConfigUpdate(BaseModel):
    display_name: str
    is_enabled: bool = False
    is_sandbox: bool = True
    api_base_url: str | None = None
    webhook_secret: str | None = None
    config: dict | None = None


class EddUpdate(BaseModel):
    status: str
    resolution_notes: str | None = None


class MfaVerify(BaseModel):
    code: str


@router.post("/exchange-rates/v2", status_code=201)
def create_rate_v2(data: ExchangeRateCreateV2, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rate = create_exchange_rate(
        db,
        from_currency=data.from_currency,
        to_currency=data.to_currency,
        rate=data.rate,
        effective_from=data.effective_from,
        effective_to=data.effective_to,
        created_by=admin.id,
        change_reason=data.change_reason,
    )
    db.commit()
    return {"id": rate.id, "rate": str(rate.rate), "effective_from": str(rate.effective_from)}


@router.get("/exchange-rates/history")
def rate_history(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 50):
    rows = list_rate_history(db, limit)
    return [
        {
            "id": r.id,
            "from_currency": r.from_currency,
            "to_currency": r.to_currency,
            "rate": str(r.rate),
            "effective_from": str(r.effective_from),
            "effective_to": str(r.effective_to) if r.effective_to else None,
            "change_reason": r.change_reason,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.post("/fee-rules/v2", status_code=201)
def create_fee_v2(data: FeeRuleCreateV2, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rule = FeeRule(**data.model_dump(), created_by=admin.id, is_active=True)
    db.add(rule)
    db.commit()
    return {"id": rule.id, "name": rule.name}


@router.get("/fee-rules/v2")
def list_fees_v2(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rules = db.query(FeeRule).order_by(FeeRule.priority.desc(), FeeRule.min_amount_zar.asc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "min_amount_zar": str(r.min_amount_zar),
            "max_amount_zar": str(r.max_amount_zar) if r.max_amount_zar else None,
            "fee_type": r.fee_type,
            "fee_value": str(r.fee_value),
            "destination_country": r.destination_country,
            "payment_method_id": r.payment_method_id,
            "provider_id": r.provider_id,
            "priority": r.priority,
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.get("/compliance/edd")
def list_edd_cases(admin: AdminUser, db: Annotated[Session, Depends(get_db)], status_filter: str | None = None):
    query = db.query(EnhancedDueDiligenceCase).order_by(EnhancedDueDiligenceCase.created_at.desc())
    if status_filter:
        try:
            query = query.filter(EnhancedDueDiligenceCase.status == EddStatus(status_filter))
        except ValueError:
            pass
    cases = query.limit(100).all()
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "transfer_id": c.transfer_id,
            "status": c.status.value,
            "risk_score": c.risk_score,
            "reason": c.reason,
            "aml_flags": c.aml_flags,
            "created_at": c.created_at.isoformat(),
        }
        for c in cases
    ]


@router.patch("/compliance/edd/{case_id}")
def update_edd_case(case_id: int, data: EddUpdate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    case = db.query(EnhancedDueDiligenceCase).filter(EnhancedDueDiligenceCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="EDD case not found")
    case.status = EddStatus(data.status)
    case.assigned_to = admin.id
    if data.resolution_notes:
        case.resolution_notes = data.resolution_notes
    db.commit()
    return {"message": "EDD case updated"}


@router.get("/providers/config")
def list_provider_configs(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    configs = db.query(ProviderConfig).order_by(ProviderConfig.provider_code).all()
    return [
        {
            "id": c.id,
            "provider_code": c.provider_code,
            "provider_type": c.provider_type,
            "display_name": c.display_name,
            "is_enabled": c.is_enabled,
            "is_sandbox": c.is_sandbox,
            "api_base_url": c.api_base_url,
            "has_webhook_secret": bool(c.webhook_secret),
            "config": c.config,
        }
        for c in configs
    ]


@router.put("/providers/config/{provider_code}")
def upsert_provider_config(
    provider_code: str,
    data: ProviderConfigUpdate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
):
    config = db.query(ProviderConfig).filter(ProviderConfig.provider_code == provider_code).first()
    provider_type = "payment" if provider_code in ("pay_at", "easy_pay", "eft", "stitch", "ozow") else "remittance"
    if not config:
        config = ProviderConfig(provider_code=provider_code, provider_type=provider_type, display_name=data.display_name)
        db.add(config)
    config.display_name = data.display_name
    config.is_enabled = data.is_enabled
    config.is_sandbox = data.is_sandbox
    config.api_base_url = data.api_base_url
    if data.webhook_secret:
        config.webhook_secret = data.webhook_secret
    config.config = data.config
    config.updated_by = admin.id
    db.commit()
    return {"message": "Provider configuration saved"}


@router.get("/notifications/logs")
def notification_logs(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 100):
    logs = db.query(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "template_code": l.template_code,
            "channel": l.channel.value,
            "recipient": l.recipient,
            "status": l.status.value,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]


@router.get("/notifications/templates")
def list_templates(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = db.query(NotificationTemplate).order_by(NotificationTemplate.code).all()
    return [
        {
            "id": t.id,
            "code": t.code,
            "name": t.name,
            "channel": t.channel.value if hasattr(t.channel, "value") else t.channel,
            "is_active": t.is_active,
        }
        for t in rows
    ]


@router.get("/security/audit")
def security_audit_logs(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 100):
    logs = db.query(SecurityAuditLog).order_by(SecurityAuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "event_type": l.event_type.value,
            "ip_address": l.ip_address,
            "details": l.details,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]


@router.get("/security/sessions")
def list_sessions(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    sessions = (
        db.query(UserSession)
        .filter(UserSession.is_revoked.is_(False))
        .order_by(UserSession.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "ip_address": s.ip_address,
            "created_at": s.created_at.isoformat(),
            "expires_at": s.expires_at.isoformat(),
        }
        for s in sessions
    ]


@router.post("/security/mfa/setup")
def mfa_setup(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    mfa, uri = setup_mfa(db, admin.id)
    db.commit()
    return {"provisioning_uri": uri, "message": "Scan QR in authenticator app, then verify with /mfa/enable"}


@router.post("/security/mfa/enable")
def mfa_enable(data: MfaVerify, admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    if not enable_mfa(db, admin.id, data.code):
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    log_security_event(db, event_type=SecurityEventType.MFA_ENABLED, user_id=admin.id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "MFA enabled"}


@router.post("/security/sessions/revoke-all")
def revoke_sessions(admin: AdminUser, db: Annotated[Session, Depends(get_db)], user_id: int = Query(...)):
    count = revoke_all_sessions(db, user_id)
    db.commit()
    return {"revoked": count}
