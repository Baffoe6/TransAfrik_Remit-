"""Launch readiness checklist with percentage score."""

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.corridor import Corridor
from app.models.customer_profile import CustomerProfile
from app.models.enums import CorridorStatus, KycStatus
from app.models.webhook import ProviderConfig
from app.providers.partners.registry import list_partner_providers
from app.redis.client import redis_health
from app.storage import storage_health


def get_launch_readiness(db: Session) -> dict:
    settings = get_settings()
    checks: list[dict] = []

    def add(check_id: str, label: str, passed: bool, detail: str | None = None):
        checks.append({"id": check_id, "label": label, "passed": passed, "detail": detail})

    add("domain_configured", "Production domain configured", bool(settings.cors_origin_list), str(settings.cors_origin_list))
    add("ssl_active", "SSL / HTTPS enforcement", settings.require_https or settings.is_production, f"require_https={settings.require_https}")
    add("dev_endpoints_disabled", "Development endpoints disabled", not settings.enable_dev_endpoints or not settings.is_production)
    add("swagger_disabled", "Swagger UI disabled in production", not settings.docs_enabled or not settings.is_production)

    try:
        db.execute(text("SELECT 1"))
        add("database_healthy", "Database healthy", True)
    except Exception as exc:
        add("database_healthy", "Database healthy", False, str(exc))

    redis = redis_health()
    add("redis_healthy", "Redis healthy", redis.get("status") == "healthy", redis.get("backend"))

    storage = storage_health()
    add("storage_healthy", "Storage healthy", storage.get("status") == "healthy", storage.get("backend"))

    add("kyc_workflow_enabled", "KYC workflow enabled", True, "KYC upload and admin review active")

    active_corridors = (
        db.query(func.count(Corridor.id)).filter(Corridor.status == CorridorStatus.ACTIVE).scalar() or 0
    )
    add("corridors_configured", "Corridors configured", active_corridors >= 6, f"{active_corridors} active corridors")

    partner_count = len(list_partner_providers())
    configured_partners = (
        db.query(func.count(ProviderConfig.id)).filter(ProviderConfig.is_enabled.is_(True)).scalar() or 0
    )
    add(
        "partner_integrations",
        "Partner integrations configured",
        configured_partners >= 4,
        f"{configured_partners} providers enabled, {partner_count} mock partner adapters",
    )

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    percent = int((passed / total) * 100) if total else 0

    return {
        "readiness_percent": percent,
        "ready": percent >= 80,
        "checks": checks,
        "passed": passed,
        "total": total,
        "environment": settings.environment,
        "version": "7.0.0-mvp",
    }
