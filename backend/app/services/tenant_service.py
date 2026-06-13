from sqlalchemy.orm import Session

from app.models.tenant import Tenant


def get_default_tenant(db: Session) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.slug == "transafrik", Tenant.is_active.is_(True)).first()


def get_tenant_by_domain(db: Session, domain: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.domain == domain, Tenant.is_active.is_(True)).first()


def list_tenants(db: Session) -> list[Tenant]:
    return db.query(Tenant).order_by(Tenant.name).all()


def tenant_brand_config(tenant: Tenant) -> dict:
    return {
        "id": tenant.id,
        "name": tenant.name,
        "slug": tenant.slug,
        "logo_url": tenant.logo_url,
        "domain": tenant.domain,
        "primary_color": tenant.primary_color,
        "secondary_color": tenant.secondary_color,
    }
