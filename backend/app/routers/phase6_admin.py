"""Phase 6 admin: pilot, launch checklist, compliance packs, demo, runbook, production."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.legal.content import LEGAL_PAGES
from app.models.enums import CompliancePackType, PilotCustomerStatus, UserRole
from app.models.pilot import PilotCustomer, PilotInvite
from app.models.user import User
from app.services.compliance_pack_service import generate_compliance_pack
from app.services.demo_mode_service import disable_demo_mode, enable_demo_mode, get_demo_journeys
from app.services.launch_checklist_service import get_launch_checklist
from app.services.operations_audit import log_operations_action
from app.services.pilot_service import (
    approve_pilot_customer,
    create_invite,
    get_pilot_settings,
)
from app.services.production_readiness import migration_safety_check, validate_production_config
from app.services.provider_credential_service import (
    run_provider_health_for_code,
    simulate_webhook_url,
    verify_signature_hmac,
    validate_provider_credentials,
)
from app.services.support_ops_service import get_escalation_queue, get_sla_breaches
from app.models.enums import OperationsAuditCategory

router = APIRouter(prefix="/admin", tags=["Admin Phase 6"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]

RUNBOOK = [
    {"id": "process_transfer", "title": "How to Process a Transfer", "steps": ["Verify payment in Payments > Verify", "Check compliance queue", "Approve transfer for processing", "Export Mukuru batch or submit via provider", "Update transfer status"]},
    {"id": "verify_payment", "title": "How to Verify Payment", "steps": ["Open Admin > Payments > Verify", "Match reference to transfer", "Confirm amount and payer details", "Mark payment as verified"]},
    {"id": "approve_compliance", "title": "How to Approve Compliance", "steps": ["Review KYC documents in Admin > KYC", "Check AML risk score", "Clear or escalate EDD cases", "Approve beneficiary if required"]},
    {"id": "export_mukuru", "title": "How to Export Mukuru Batch", "steps": ["Go to Admin > Mukuru", "Select ready-for-processing transfers", "Generate CSV/Excel batch", "Upload to Mukuru portal", "Mark batch as submitted"]},
    {"id": "reconcile_settlement", "title": "How to Reconcile Settlement", "steps": ["Open Admin > Settlement", "Import provider settlement report", "Run auto-reconcile", "Investigate variances"]},
    {"id": "failed_transfer", "title": "How to Handle Failed Transfer", "steps": ["Check provider status and error message", "Contact partner support if needed", "Update customer via support ticket", "Initiate refund if funds not disbursed", "Log in operations audit"]},
]


class PilotSettingsUpdate(BaseModel):
    pilot_mode_enabled: bool | None = None
    invite_only_registration: bool | None = None
    require_admin_approval: bool | None = None
    default_max_transfer_zar: Decimal | None = None
    default_daily_transfer_limit: int | None = None
    default_monthly_volume_zar: Decimal | None = None
    default_allowed_corridors: list[str] | None = None


class PilotInviteCreate(BaseModel):
    email: str | None = None
    max_uses: int = 1
    expires_days: int | None = 30


class PilotApprove(BaseModel):
    notes: str | None = None


class PilotLimitsUpdate(BaseModel):
    max_transfer_zar: Decimal | None = None
    daily_transfer_limit: int | None = None
    monthly_volume_zar: Decimal | None = None
    allowed_corridors: list[str] | None = None


class CompliancePackRequest(BaseModel):
    pack_type: str
    user_id: int | None = None
    transfer_id: int | None = None
    batch_id: int | None = None


class WebhookTestRequest(BaseModel):
    webhook_url: str
    secret: str | None = None


class SignatureTestRequest(BaseModel):
    secret: str
    payload: str
    signature: str


@router.get("/pilot/settings")
def pilot_settings(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    s = get_pilot_settings(db)
    return {
        "pilot_mode_enabled": s.pilot_mode_enabled,
        "invite_only_registration": s.invite_only_registration,
        "require_admin_approval": s.require_admin_approval,
        "default_max_transfer_zar": str(s.default_max_transfer_zar),
        "default_daily_transfer_limit": s.default_daily_transfer_limit,
        "default_monthly_volume_zar": str(s.default_monthly_volume_zar),
        "default_allowed_corridors": s.default_allowed_corridors,
        "demo_mode_enabled": s.demo_mode_enabled,
    }


@router.patch("/pilot/settings")
def update_pilot_settings(data: PilotSettingsUpdate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    s = get_pilot_settings(db)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    return {"updated": True}


@router.get("/pilot/customers")
def list_pilot_customers(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = db.query(PilotCustomer).order_by(PilotCustomer.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "status": p.status.value,
            "invite_code_used": p.invite_code_used,
            "max_transfer_zar": str(p.max_transfer_zar) if p.max_transfer_zar else None,
            "created_at": p.created_at.isoformat(),
        }
        for p in rows
    ]


@router.post("/pilot/invites", status_code=201)
def create_pilot_invite(data: PilotInviteCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    invite = create_invite(db, email=data.email, max_uses=data.max_uses, expires_days=data.expires_days, created_by=admin.id)
    db.commit()
    return {"id": invite.id, "invite_code": invite.invite_code}


@router.get("/pilot/invites")
def list_pilot_invites(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = db.query(PilotInvite).order_by(PilotInvite.created_at.desc()).all()
    return [{"id": i.id, "code": i.invite_code, "email": i.email, "status": i.status.value, "uses": i.uses_count} for i in rows]


@router.post("/pilot/customers/{pilot_id}/approve")
def approve_pilot(pilot_id: int, data: PilotApprove, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    pilot = db.query(PilotCustomer).filter(PilotCustomer.id == pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot customer not found")
    approve_pilot_customer(db, pilot, admin.id, data.notes)
    db.commit()
    return {"status": "approved"}


@router.patch("/pilot/customers/{pilot_id}/limits")
def update_pilot_limits(pilot_id: int, data: PilotLimitsUpdate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    pilot = db.query(PilotCustomer).filter(PilotCustomer.id == pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(pilot, k, v)
    db.commit()
    return {"updated": True}


@router.get("/launch-checklist")
def launch_checklist(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_launch_checklist(db)


@router.get("/production-readiness")
def production_readiness(admin: AdminUser):
    return validate_production_config()


@router.get("/migration-safety")
def migration_safety(admin: AdminUser):
    return migration_safety_check("007")


@router.post("/compliance-packs/generate")
def generate_pack(data: CompliancePackRequest, admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    pack_type = CompliancePackType(data.pack_type)
    kwargs = {k: v for k, v in {"user_id": data.user_id, "transfer_id": data.transfer_id, "batch_id": data.batch_id}.items() if v}
    path = generate_compliance_pack(db, pack_type, **kwargs)
    log_operations_action(db, category=OperationsAuditCategory.COMPLIANCE_PACK, action="pack_generated", entity_type="compliance_pack", user_id=admin.id, details={"type": data.pack_type}, ip_address=get_client_ip(request))
    db.commit()
    return {"file_path": path, "download_url": f"/api/v1/admin/compliance-packs/download?path={path}"}


@router.get("/compliance-packs/download")
def download_pack(admin: AdminUser, path: str):
    import os
    if not os.path.isfile(path) or "compliance_packs" not in path.replace("\\", "/"):
        raise HTTPException(status_code=404, detail="Pack not found")
    return FileResponse(path, filename=os.path.basename(path))


@router.post("/providers/{provider_code}/validate")
def validate_provider(provider_code: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return validate_provider_credentials(db, provider_code)


@router.post("/providers/{provider_code}/health")
def provider_health(provider_code: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    result = run_provider_health_for_code(db, provider_code)
    db.commit()
    return result


@router.post("/providers/webhook-test")
def webhook_test(data: WebhookTestRequest, admin: AdminUser):
    return simulate_webhook_url("generic", data.webhook_url, data.secret)


@router.post("/providers/signature-test")
def signature_test(data: SignatureTestRequest, admin: AdminUser):
    return verify_signature_hmac(data.secret, data.payload, data.signature)


@router.get("/demo/journeys")
def demo_journeys(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_demo_journeys()


@router.post("/demo/enable")
def demo_enable(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    enable_demo_mode(db)
    db.commit()
    return {"demo_mode": True}


@router.post("/demo/disable")
def demo_disable(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    disable_demo_mode(db)
    db.commit()
    return {"demo_mode": False}


@router.get("/runbook")
def operations_runbook(admin: AdminUser):
    return {"sections": RUNBOOK}


@router.get("/support/escalations")
def support_escalations(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = get_escalation_queue(db)
    return [{"id": t.id, "subject": t.subject, "priority": t.priority.value, "sla_due_at": t.sla_due_at.isoformat() if t.sla_due_at else None} for t in rows]


@router.get("/support/sla-breaches")
def support_sla_breaches(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = get_sla_breaches(db)
    return [{"id": t.id, "subject": t.subject, "sla_due_at": t.sla_due_at.isoformat() if t.sla_due_at else None} for t in rows]
