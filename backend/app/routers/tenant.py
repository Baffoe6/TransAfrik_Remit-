from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.services.tenant_service import get_default_tenant, get_tenant_by_domain, list_tenants, tenant_brand_config

router = APIRouter(prefix="/tenant", tags=["Multi-Tenant"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.FOUNDER))]


@router.get("/brand")
def get_brand_config(
    db: Annotated[Session, Depends(get_db)],
    host: str | None = Header(default=None, alias="X-Tenant-Domain"),
):
    tenant = get_tenant_by_domain(db, host) if host else get_default_tenant(db)
    if not tenant:
        return {
            "name": "TransAfrik Remit",
            "slug": "transafrik",
            "primary_color": "#1B5E3B",
            "secondary_color": "#C9A227",
        }
    return tenant_brand_config(tenant)


@router.get("/list")
def admin_list_tenants(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return [tenant_brand_config(t) for t in list_tenants(db)]
