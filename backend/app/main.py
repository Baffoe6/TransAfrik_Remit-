from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.rate_limit import limiter
from app.routers import (
    admin,
    analytics,
    auth,
    beneficiaries,
    kyc,
    payments,
    phase2_admin,
    phase3_admin,
    phase4_admin,
    phase5_admin,
    phase6_admin,
    phase61_admin,
    pilot,
    legal,
    profile,
    wallet,
    agent,
    referral,
    support,
    tenant,
    transfers,
    webhooks,
    whatsapp_bot,
)
from app.middleware.production import HttpsEnforcementMiddleware
from app.redis.client import redis_health
from app.storage import storage_health

settings = get_settings()

DISCLAIMER = (
    "TransAfrik Remit is a customer-facing remittance facilitation platform operated by "
    "IPAYGO (Pty) Ltd. Transfers are processed through approved third-party payment "
    "and remittance partners."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.utils.file_storage import ensure_upload_dir

    ensure_upload_dir()
    yield


app = FastAPI(
    title="TransAfrik Remit API",
    description=f"Remittance platform API by IPAYGO (Pty) Ltd.\n\n{DISCLAIMER}",
    version="6.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(HttpsEnforcementMiddleware)

_cors_kwargs: dict = {
    "allow_origins": settings.cors_origin_list,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.effective_cors_origin_regex:
    _cors_kwargs["allow_origin_regex"] = settings.effective_cors_origin_regex

app.add_middleware(CORSMiddleware, **_cors_kwargs)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(kyc.router, prefix="/api/v1")
app.include_router(beneficiaries.router, prefix="/api/v1")
app.include_router(transfers.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(phase2_admin.router, prefix="/api/v1")
app.include_router(phase3_admin.router, prefix="/api/v1")
app.include_router(phase4_admin.router, prefix="/api/v1")
app.include_router(phase5_admin.router, prefix="/api/v1")
app.include_router(phase6_admin.router, prefix="/api/v1")
app.include_router(phase61_admin.router, prefix="/api/v1")
app.include_router(pilot.router, prefix="/api/v1")
app.include_router(legal.router, prefix="/api/v1")
app.include_router(wallet.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(referral.router, prefix="/api/v1")
app.include_router(tenant.router, prefix="/api/v1")
app.include_router(whatsapp_bot.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


@app.get("/health")
@limiter.limit("60/minute")
def health(request: Request):
    from sqlalchemy import text

    from app.database import SessionLocal

    db_status = "healthy"
    db_error = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as exc:
        db_status = "unhealthy"
        db_error = str(exc)

    return {
        "status": "healthy",
        "service": "transafrik-remit-api",
        "version": "6.1.0",
        "environment": settings.environment,
        "checks": {
            "database": {"status": db_status, "error": db_error},
            "redis": redis_health(),
            "storage": storage_health(),
        },
    }


@app.get("/api/v1/disclaimer")
def get_disclaimer():
    return {"disclaimer": DISCLAIMER, "operator": "IPAYGO (Pty) Ltd", "platform": "TransAfrik Remit"}
