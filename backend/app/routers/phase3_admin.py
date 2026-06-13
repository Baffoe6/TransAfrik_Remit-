"""Phase 3 admin routes: Mukuru operations, treasury, settlement, operations audit."""

from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.models.enums import OperationsAuditCategory, UserRole
from app.models.mukuru_operations import MukuruBatch
from app.models.operations_audit import OperationsAuditLog
from app.models.user import User
from app.services.mukuru_batch_service import (
    approve_batch,
    create_batch_from_transfers,
    get_batch_reconciliation_summary,
    record_mukuru_settlement,
    reject_batch,
    submit_batch,
)
from app.services.operations_audit import log_operations_action
from app.services.settlement_service import get_settlement_dashboard, record_payment_settlement, reconcile_provider_from_references
from app.services.treasury_service import get_treasury_dashboard
from app.utils.file_storage import ensure_upload_dir

router = APIRouter(prefix="/admin", tags=["Admin Phase 3"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER))]


class BatchCreateRequest(BaseModel):
    transfer_ids: list[int]
    format: str = "csv"


class BatchRejectRequest(BaseModel):
    reason: str


class MukuruSettlementCreate(BaseModel):
    settlement_reference: str
    settlement_date: date
    amount_zar: Decimal = Field(gt=0)
    amount_ghs: Decimal = Field(gt=0)
    batch_id: int | None = None
    transfer_count: int = 0
    notes: str | None = None


class PaymentSettlementCreate(BaseModel):
    provider: str
    settlement_date: date
    expected_amount_zar: Decimal = Field(ge=0)
    collected_amount_zar: Decimal = Field(ge=0)
    transaction_count: int = 0
    notes: str | None = None


@router.post("/mukuru/batches", status_code=201)
def create_mukuru_batch(
    data: BatchCreateRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    try:
        batch = create_batch_from_transfers(
            db,
            transfer_ids=data.transfer_ids,
            created_by=admin.id,
            export_format=data.format,
            ip_address=get_client_ip(request),
        )
        db.commit()
        return {
            "id": batch.id,
            "batch_id": batch.batch_id,
            "status": batch.status.value,
            "transfer_count": batch.transfer_count,
            "total_amount_zar": str(batch.total_amount_zar),
            "download_url": f"/api/v1/admin/mukuru/batches/{batch.batch_id}/download",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mukuru/batches")
def list_mukuru_batches(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 50):
    batches = db.query(MukuruBatch).order_by(MukuruBatch.created_at.desc()).limit(limit).all()
    return [
        {
            "id": b.id,
            "batch_id": b.batch_id,
            "status": b.status.value,
            "transfer_count": b.transfer_count,
            "total_amount_zar": str(b.total_amount_zar),
            "total_amount_ghs": str(b.total_amount_ghs),
            "file_format": b.file_format,
            "created_at": b.created_at.isoformat(),
            "approved_at": b.approved_at.isoformat() if b.approved_at else None,
            "submitted_at": b.submitted_at.isoformat() if b.submitted_at else None,
            "reconciled_at": b.reconciled_at.isoformat() if b.reconciled_at else None,
        }
        for b in batches
    ]


@router.get("/mukuru/batches/{batch_id}")
def get_mukuru_batch(batch_id: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    batch = db.query(MukuruBatch).filter(MukuruBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    items = [
        {
            "transfer_id": i.transfer_id,
            "amount_zar": str(i.amount_zar),
            "amount_ghs": str(i.amount_ghs),
            "status": i.status,
            "provider_reference": i.provider_reference,
        }
        for i in batch.items
    ]
    return {
        "id": batch.id,
        "batch_id": batch.batch_id,
        "status": batch.status.value,
        "transfer_count": batch.transfer_count,
        "total_amount_zar": str(batch.total_amount_zar),
        "items": items,
        "notes": batch.notes,
    }


@router.post("/mukuru/batches/{batch_id}/approve")
def approve_mukuru_batch(batch_id: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    batch = db.query(MukuruBatch).filter(MukuruBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    try:
        approve_batch(db, batch, approved_by=admin.id, ip_address=get_client_ip(request))
        db.commit()
        return {"message": "Batch approved", "status": batch.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mukuru/batches/{batch_id}/submit")
def submit_mukuru_batch(batch_id: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    batch = db.query(MukuruBatch).filter(MukuruBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    try:
        submit_batch(db, batch, submitted_by=admin.id, ip_address=get_client_ip(request))
        db.commit()
        return {"message": "Batch submitted to Mukuru", "status": batch.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mukuru/batches/{batch_id}/reject")
def reject_mukuru_batch(
    batch_id: str,
    data: BatchRejectRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    batch = db.query(MukuruBatch).filter(MukuruBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    reject_batch(db, batch, rejected_by=admin.id, reason=data.reason, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Batch rejected"}


@router.get("/mukuru/batches/{batch_id}/download")
def download_mukuru_batch(batch_id: str, admin: AdminUser):
    batch_dir = ensure_upload_dir() / "batches"
    for ext in ("csv", "xlsx"):
        path = batch_dir / f"{batch_id}.{ext}"
        if path.exists():
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if ext == "xlsx" else "text/csv"
            return FileResponse(path, filename=f"{batch_id}.{ext}", media_type=media)
    raise HTTPException(status_code=404, detail="Batch file not found")


@router.get("/mukuru/reconciliation")
def mukuru_reconciliation(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_batch_reconciliation_summary(db)


@router.post("/mukuru/settlements", status_code=201)
def create_mukuru_settlement(
    data: MukuruSettlementCreate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    settlement = record_mukuru_settlement(
        db,
        settlement_reference=data.settlement_reference,
        settlement_date=data.settlement_date,
        amount_zar=data.amount_zar,
        amount_ghs=data.amount_ghs,
        batch_id=data.batch_id,
        transfer_count=data.transfer_count,
        recorded_by=admin.id,
        notes=data.notes,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"id": settlement.id, "status": settlement.status.value, "variance_zar": str(settlement.variance_zar)}


@router.get("/treasury/dashboard")
def treasury_dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    data = get_treasury_dashboard(db)
    log_operations_action(
        db,
        category=OperationsAuditCategory.TREASURY,
        action="treasury_dashboard_viewed",
        entity_type="treasury",
        user_id=admin.id,
    )
    db.commit()
    return data


@router.get("/settlement/dashboard")
def settlement_dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_settlement_dashboard(db)


@router.post("/settlement/payment", status_code=201)
def create_payment_settlement(
    data: PaymentSettlementCreate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    settlement = record_payment_settlement(
        db,
        provider=data.provider,
        settlement_date=data.settlement_date,
        expected_amount_zar=data.expected_amount_zar,
        collected_amount_zar=data.collected_amount_zar,
        transaction_count=data.transaction_count,
        recorded_by=admin.id,
        notes=data.notes,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"id": settlement.id, "status": settlement.status.value, "variance_zar": str(settlement.variance_zar)}


@router.post("/settlement/reconcile/{provider}")
def auto_reconcile_provider(
    provider: str,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    settlement_date: date = Query(default_factory=date.today),
):
    settlement = reconcile_provider_from_references(
        db,
        provider=provider,
        settlement_date=settlement_date,
        recorded_by=admin.id,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"id": settlement.id, "collected_zar": str(settlement.collected_amount_zar)}


@router.get("/operations-audit")
def operations_audit_logs(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    category: str | None = None,
    limit: int = 100,
):
    query = db.query(OperationsAuditLog).order_by(OperationsAuditLog.created_at.desc())
    if category:
        try:
            query = query.filter(OperationsAuditLog.category == OperationsAuditCategory(category))
        except ValueError:
            pass
    logs = query.limit(limit).all()
    return [
        {
            "id": l.id,
            "category": l.category.value,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "user_id": l.user_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
