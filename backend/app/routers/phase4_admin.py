"""Phase 4 admin: founder dashboard, FX markup, retail networks."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.models.enums import FxMarkupType, FxRateSourceType, OperationsAuditCategory, UserRole
from app.models.fx import FxMarkupRule, FxRateSource
from app.models.user import User
from app.retail_network.registry import list_retail_networks
from app.services.founder_dashboard import get_founder_executive_dashboard
from app.services.operations_audit import log_operations_action

router = APIRouter(prefix="/admin", tags=["Admin Phase 4"])
FounderUser = Annotated[User, Depends(require_roles(UserRole.FOUNDER, UserRole.ADMIN))]
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]


class FxMarkupCreate(BaseModel):
    from_currency: str = "ZAR"
    to_currency: str = "GHS"
    markup_type: str = "percentage"
    markup_value: Decimal = Field(gt=0)
    priority: int = 0


class FxSourceCreate(BaseModel):
    code: str
    name: str
    source_type: str = "manual"
    priority: int = 0
    config: dict | None = None


@router.get("/founder/dashboard")
def founder_dashboard(founder: FounderUser, db: Annotated[Session, Depends(get_db)], request: Request):
    data = get_founder_executive_dashboard(db)
    log_operations_action(
        db,
        category=OperationsAuditCategory.TREASURY,
        action="founder_dashboard_viewed",
        entity_type="founder_dashboard",
        user_id=founder.id,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return data


@router.get("/fx/sources")
def list_fx_sources(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rows = db.query(FxRateSource).order_by(FxRateSource.priority.desc()).all()
    return [
        {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "source_type": s.source_type.value if hasattr(s.source_type, "value") else s.source_type,
            "is_active": s.is_active,
            "priority": s.priority,
        }
        for s in rows
    ]


@router.post("/fx/sources", status_code=201)
def create_fx_source(data: FxSourceCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    source = FxRateSource(
        code=data.code,
        name=data.name,
        source_type=FxRateSourceType(data.source_type),
        priority=data.priority,
        config=data.config,
        is_active=True,
    )
    db.add(source)
    log_operations_action(
        db,
        category=OperationsAuditCategory.FX,
        action="fx_source_created",
        entity_type="fx_rate_source",
        user_id=admin.id,
        details={"code": data.code},
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"id": source.id, "code": source.code}


@router.get("/fx/markup")
def list_fx_markup(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rules = db.query(FxMarkupRule).order_by(FxMarkupRule.priority.desc()).all()
    return [
        {
            "id": r.id,
            "from_currency": r.from_currency,
            "to_currency": r.to_currency,
            "markup_type": r.markup_type.value,
            "markup_value": str(r.markup_value),
            "priority": r.priority,
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.post("/fx/markup", status_code=201)
def create_fx_markup(data: FxMarkupCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)], request: Request):
    rule = FxMarkupRule(
        from_currency=data.from_currency,
        to_currency=data.to_currency,
        markup_type=FxMarkupType(data.markup_type),
        markup_value=data.markup_value,
        priority=data.priority,
        created_by=admin.id,
        is_active=True,
    )
    db.add(rule)
    log_operations_action(
        db,
        category=OperationsAuditCategory.FX,
        action="fx_markup_created",
        entity_type="fx_markup_rule",
        user_id=admin.id,
        details=data.model_dump(mode="json"),
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"id": rule.id}


@router.get("/retail-networks")
def retail_networks(admin: AdminUser):
    return {"networks": list_retail_networks()}
