"""Phase 5 admin: corridors, FX sources, documents, operations, board dashboard, API keys."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.models.corridor import Corridor, CorridorProviderRoute
from app.models.enums import ApiEnvironment, CorridorStatus, DocumentCategory, UserRole
from app.models.user import User
from app.services.api_security_service import create_api_key, list_api_keys, revoke_api_key, store_provider_secret
from app.services.corridor_service import (
    create_corridor,
    get_corridor,
    list_corridor_routes,
    list_corridors,
    set_corridor_status,
    update_corridor,
)
from app.services.document_center_service import get_document, list_documents, log_document_download, upload_document
from app.services.executive_dashboard import get_board_executive_dashboard
from app.services.fx_feed_engine import get_fx_dashboard, sync_all_active_sources, sync_fx_from_feed
from app.services.operations_audit import log_operations_action
from app.services.operations_center_service import check_provider_health, get_operations_center_dashboard
from app.services.provider_router import list_available_providers, quote_transfer
from app.providers.orchestration.interface import OrchestrationQuoteRequest
from app.models.enums import OperationsAuditCategory
from app.fx_sources.registry import list_fx_feed_providers

router = APIRouter(prefix="/admin", tags=["Admin Phase 5"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]
FounderUser = Annotated[User, Depends(require_roles(UserRole.FOUNDER, UserRole.ADMIN))]


class CorridorCreate(BaseModel):
    code: str
    source_country: str = "ZA"
    destination_country: str
    destination_currency: str
    provider_code: str
    fee_rule_id: int | None = None
    fx_markup_rule_id: int | None = None
    priority: int = 0


class CorridorUpdate(BaseModel):
    provider_code: str | None = None
    fee_rule_id: int | None = None
    fx_markup_rule_id: int | None = None
    priority: int | None = None
    status: str | None = None


class ProviderQuoteRequest(BaseModel):
    source_country: str = "ZA"
    destination_country: str
    send_amount: Decimal = Field(gt=0)


class ApiKeyCreate(BaseModel):
    name: str
    environment: str = "development"
    scopes: list[str] | None = None


class ProviderSecretCreate(BaseModel):
    provider_code: str
    secret_name: str
    value: str
    environment: str = "development"


@router.get("/board/dashboard")
def board_dashboard(founder: FounderUser, db: Annotated[Session, Depends(get_db)], request: Request):
    data = get_board_executive_dashboard(db)
    log_operations_action(
        db,
        category=OperationsAuditCategory.TREASURY,
        action="board_dashboard_viewed",
        entity_type="executive_dashboard",
        user_id=founder.id,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return data


@router.get("/corridors")
def admin_list_corridors(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = list_corridors(db)
    return [
        {
            "id": c.id,
            "code": c.code,
            "source_country": c.source_country,
            "destination_country": c.destination_country,
            "destination_currency": c.destination_currency,
            "provider_code": c.provider_code,
            "status": c.status.value if hasattr(c.status, "value") else c.status,
            "fee_rule_id": c.fee_rule_id,
            "fx_markup_rule_id": c.fx_markup_rule_id,
            "priority": c.priority,
        }
        for c in rows
    ]


@router.post("/corridors", status_code=201)
def admin_create_corridor(data: CorridorCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    corridor = create_corridor(db, data.model_dump(), user_id=admin.id)
    db.commit()
    return {"id": corridor.id, "code": corridor.code}


@router.patch("/corridors/{corridor_id}")
def admin_update_corridor(
    corridor_id: int,
    data: CorridorUpdate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
):
    corridor = get_corridor(db, corridor_id)
    if not corridor:
        raise HTTPException(status_code=404, detail="Corridor not found")
    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        set_corridor_status(db, corridor, CorridorStatus(updates.pop("status")), user_id=admin.id)
    if updates:
        update_corridor(db, corridor, updates, user_id=admin.id)
    db.commit()
    return {"id": corridor.id, "status": corridor.status.value}


@router.get("/corridors/{corridor_id}/routes")
def admin_corridor_routes(corridor_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    routes = list_corridor_routes(db, corridor_id)
    return [
        {
            "id": r.id,
            "provider_code": r.provider_code,
            "priority": r.priority,
            "cost_score": r.cost_score,
            "is_available": r.is_available,
        }
        for r in routes
    ]


@router.get("/fx-sources/dashboard")
def fx_sources_dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_fx_dashboard(db)


@router.post("/fx-sources/sync")
def trigger_fx_sync(admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    runs = sync_all_active_sources(db)
    log_operations_action(
        db,
        category=OperationsAuditCategory.FX,
        action="fx_feed_sync_triggered",
        entity_type="fx_sync",
        user_id=admin.id,
        ip_address=get_client_ip(request),
        details={"runs": len(runs)},
    )
    db.commit()
    return {"runs": [{"source": r.source_code, "success": r.success, "pairs": r.pairs_synced} for r in runs]}


@router.post("/fx-sources/sync/{provider_code}")
def sync_single_fx_provider(provider_code: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    if provider_code not in list_fx_feed_providers():
        raise HTTPException(status_code=400, detail="Unknown FX feed provider")
    run = sync_fx_from_feed(db, source_code=provider_code)
    db.commit()
    return {"success": run.success, "pairs_synced": run.pairs_synced}


@router.get("/documents")
def admin_list_documents(admin: AdminUser, db: Annotated[Session, Depends(get_db)], category: str | None = None):
    cat = DocumentCategory(category) if category else None
    docs = list_documents(db, category=cat)
    return [
        {
            "id": d.id,
            "category": d.category.value if hasattr(d.category, "value") else d.category,
            "title": d.title,
            "version": d.version,
            "expires_at": d.expires_at.isoformat() if d.expires_at else None,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.post("/documents", status_code=201)
async def admin_upload_document(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(...),
    title: str = Form(...),
    description: str | None = Form(None),
    expires_at: str | None = Form(None),
):
    exp = datetime.fromisoformat(expires_at) if expires_at else None
    record = upload_document(
        db,
        file=file,
        category=DocumentCategory(category),
        title=title,
        description=description,
        uploaded_by=admin.id,
        expires_at=exp,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"id": record.id, "title": record.title, "version": record.version}


@router.get("/documents/{document_id}/download")
def admin_download_document(
    document_id: int,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    from fastapi.responses import FileResponse

    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    log_document_download(db, doc, admin.id, ip_address=get_client_ip(request))
    db.commit()
    return FileResponse(doc.file_path, filename=doc.file_name)


@router.get("/operations")
def operations_center(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_operations_center_dashboard(db)


@router.post("/operations/health-check")
def run_health_check(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    checks = check_provider_health(db)
    db.commit()
    return {"checked": len(checks)}


@router.get("/orchestration/providers")
def orchestration_providers(admin: AdminUser):
    return {"providers": list_available_providers()}


@router.post("/orchestration/quote")
def orchestration_quote(data: ProviderQuoteRequest, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    quote = quote_transfer(
        db,
        OrchestrationQuoteRequest(
            source_country=data.source_country,
            destination_country=data.destination_country,
            send_amount=data.send_amount,
        ),
        user_id=admin.id,
    )
    db.commit()
    return {
        "provider": quote.provider_code,
        "send_amount": str(quote.send_amount),
        "receive_amount": str(quote.receive_amount),
        "exchange_rate": str(quote.exchange_rate),
        "fee_amount": str(quote.fee_amount),
    }


@router.get("/api-keys")
def admin_list_api_keys(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    keys = list_api_keys(db)
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "environment": k.environment.value,
            "status": k.status.value,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
        }
        for k in keys
    ]


@router.post("/api-keys", status_code=201)
def admin_create_api_key(data: ApiKeyCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    record, raw_key = create_api_key(
        db,
        name=data.name,
        environment=ApiEnvironment(data.environment),
        scopes=data.scopes,
        created_by=admin.id,
    )
    db.commit()
    return {"id": record.id, "key_prefix": record.key_prefix, "api_key": raw_key}


@router.delete("/api-keys/{key_id}")
def admin_revoke_api_key(key_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    if not revoke_api_key(db, key_id, admin.id):
        raise HTTPException(status_code=404, detail="API key not found")
    db.commit()
    return {"revoked": True}


@router.post("/provider-secrets", status_code=201)
def admin_store_secret(data: ProviderSecretCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    record = store_provider_secret(
        db,
        provider_code=data.provider_code,
        secret_name=data.secret_name,
        value=data.value,
        environment=ApiEnvironment(data.environment),
    )
    db.commit()
    return {"id": record.id, "provider_code": record.provider_code}
