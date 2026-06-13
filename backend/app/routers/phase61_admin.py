"""Phase 6.1 admin: credential vault, infrastructure health, integration harness."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.enums import ApiEnvironment, UserRole
from app.models.user import User
from app.redis.client import redis_health
from app.redis.otp_store import store_otp, verify_otp
from app.redis.rate_limit import check_rate_limit
from app.redis.webhook_queue import peek_queue, queue_depth
from app.services.credential_vault import (
    deactivate_credential,
    get_provider_credentials,
    list_credentials,
    store_credential,
    validate_stored_credentials,
)
from app.storage import storage_health
from app.webhooks.security import verify_hmac_signature

router = APIRouter(prefix="/admin", tags=["Admin Phase 6.1"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]


class VaultCredentialCreate(BaseModel):
    provider_code: str
    secret_name: str
    value: str = Field(min_length=1)
    environment: ApiEnvironment = ApiEnvironment.DEVELOPMENT
    credential_type: str = "api_key"


class OtpTestRequest(BaseModel):
    identifier: str
    code: str


class HmacVerifyRequest(BaseModel):
    payload: str
    signature: str
    secret: str


@router.get("/vault/credentials")
def vault_list_credentials(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    provider_code: str | None = None,
    environment: ApiEnvironment | None = None,
):
    return {"credentials": list_credentials(db, provider_code, environment)}


@router.post("/vault/credentials")
def vault_store_credential(data: VaultCredentialCreate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    record = store_credential(
        db,
        provider_code=data.provider_code,
        secret_name=data.secret_name,
        value=data.value,
        environment=data.environment,
        credential_type=data.credential_type,
    )
    db.commit()
    return {"id": record.id, "provider_code": record.provider_code, "secret_name": record.secret_name, "stored": True}


@router.post("/vault/credentials/{credential_id}/deactivate")
def vault_deactivate(credential_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    if not deactivate_credential(db, credential_id):
        raise HTTPException(status_code=404, detail="Credential not found")
    db.commit()
    return {"deactivated": True}


@router.post("/vault/validate/{provider_code}")
def vault_validate(provider_code: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    result = validate_stored_credentials(db, provider_code)
    db.commit()
    return result


@router.get("/vault/credentials/{provider_code}/resolve")
def vault_resolve(provider_code: str, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    creds = get_provider_credentials(db, provider_code)
    return {
        "provider_code": provider_code,
        "secret_names": list(creds.keys()),
        "count": len(creds),
    }


@router.get("/infrastructure/health")
def infrastructure_health(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    from sqlalchemy import text

    db_ok = True
    db_error = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_ok = False
        db_error = str(exc)

    return {
        "database": {"status": "healthy" if db_ok else "unhealthy", "error": db_error},
        "redis": redis_health(),
        "storage": storage_health(),
        "webhook_queue_depth": queue_depth(),
    }


@router.get("/infrastructure/webhook-queue")
def infrastructure_webhook_queue(admin: AdminUser, limit: int = 20):
    return {"depth": queue_depth(), "items": peek_queue(limit)}


@router.post("/infrastructure/test-otp")
def infrastructure_test_otp(data: OtpTestRequest, admin: AdminUser):
    store_otp("test", data.identifier, data.code, ttl=120)
    verified = verify_otp("test", data.identifier, data.code)
    return {"stored": True, "verified": verified}


@router.post("/infrastructure/test-rate-limit")
def infrastructure_test_rate_limit(admin: AdminUser, key: str = "test", limit: int = 3, window: int = 60):
    allowed, count = check_rate_limit(key, limit, window)
    return {"allowed": allowed, "count": count, "limit": limit, "window_seconds": window}


@router.post("/infrastructure/verify-hmac")
def infrastructure_verify_hmac(data: HmacVerifyRequest, admin: AdminUser):
    valid = verify_hmac_signature(data.payload.encode(), data.signature, data.secret)
    return {"valid": valid}
