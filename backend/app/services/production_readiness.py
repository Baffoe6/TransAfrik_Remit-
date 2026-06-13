"""Production deployment readiness checks."""

from app.config import get_settings


REQUIRED_PRODUCTION_SECRETS = [
    "secret_key",
    "database_url",
]


def validate_production_config() -> dict:
    settings = get_settings()
    checks: list[dict] = []

    checks.append({
        "id": "environment",
        "label": "Environment set to production",
        "passed": settings.is_production,
        "severity": "critical",
    })
    checks.append({
        "id": "secret_key",
        "label": "SECRET_KEY changed from default",
        "passed": settings.secret_key not in ("", "change-me-in-production"),
        "severity": "critical",
    })
    checks.append({
        "id": "cors",
        "label": "CORS origins configured (no wildcard)",
        "passed": bool(settings.cors_origin_list) and "*" not in settings.cors_origins,
        "severity": "high",
    })
    checks.append({
        "id": "docs_disabled",
        "label": "API docs disabled in production",
        "passed": not settings.docs_enabled if settings.is_production else True,
        "severity": "medium",
    })
    checks.append({
        "id": "dev_endpoints",
        "label": "Dev endpoints disabled in production",
        "passed": not settings.enable_dev_endpoints if settings.is_production else True,
        "severity": "high",
    })
    checks.append({
        "id": "https",
        "label": "HTTPS enforcement enabled",
        "passed": settings.require_https if settings.is_production else True,
        "severity": "critical",
    })
    checks.append({
        "id": "api_signing",
        "label": "API signing secret configured",
        "passed": bool(settings.api_signing_secret) if settings.is_production else True,
        "severity": "medium",
    })
    checks.append({
        "id": "secure_cookies",
        "label": "Secure cookie settings",
        "passed": settings.secure_cookies if settings.is_production else True,
        "severity": "high",
    })

    passed = sum(1 for c in checks if c["passed"])
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "ready": passed == len(checks),
        "environment": settings.environment,
    }


def migration_safety_check(current_revision: str | None, head_revision: str = "011") -> dict:
    return {
        "current_revision": current_revision,
        "head_revision": head_revision,
        "up_to_date": current_revision == head_revision,
        "safe_to_deploy": current_revision == head_revision,
        "message": "Run alembic upgrade head before production deploy" if current_revision != head_revision else "Migrations up to date",
    }
