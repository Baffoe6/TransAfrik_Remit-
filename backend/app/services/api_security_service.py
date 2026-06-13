import hashlib
import hmac
import secrets
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.api_security import ApiKey, ProviderSecret, SecurityMonitorEvent
from app.models.enums import ApiEnvironment, ApiKeyStatus, OperationsAuditCategory
from app.services.operations_audit import log_operations_action


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def create_api_key(
    db: Session,
    *,
    name: str,
    environment: ApiEnvironment,
    scopes: list[str] | None,
    created_by: int,
    expires_at: datetime | None = None,
) -> tuple[ApiKey, str]:
    raw_key = f"ta_{environment.value}_{secrets.token_urlsafe(32)}"
    prefix = raw_key[:12]
    record = ApiKey(
        name=name,
        key_prefix=prefix,
        key_hash=_hash_key(raw_key),
        environment=environment,
        status=ApiKeyStatus.ACTIVE,
        scopes=scopes,
        created_by=created_by,
        expires_at=expires_at,
    )
    db.add(record)
    db.flush()
    log_operations_action(
        db,
        category=OperationsAuditCategory.API_SECURITY,
        action="api_key_created",
        entity_type="api_key",
        entity_id=record.id,
        user_id=created_by,
        details={"name": name, "environment": environment.value},
    )
    return record, raw_key


def validate_api_key(db: Session, raw_key: str) -> ApiKey | None:
    if not raw_key or len(raw_key) < 12:
        return None
    prefix = raw_key[:12]
    key_hash = _hash_key(raw_key)
    record = (
        db.query(ApiKey)
        .filter(
            ApiKey.key_prefix == prefix,
            ApiKey.key_hash == key_hash,
            ApiKey.status == ApiKeyStatus.ACTIVE,
        )
        .first()
    )
    if not record:
        return None
    if record.expires_at and record.expires_at < datetime.now(UTC):
        record.status = ApiKeyStatus.EXPIRED
        return None
    record.last_used_at = datetime.now(UTC)
    return record


def revoke_api_key(db: Session, key_id: int, revoked_by: int) -> bool:
    record = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not record:
        return False
    record.status = ApiKeyStatus.REVOKED
    log_operations_action(
        db,
        category=OperationsAuditCategory.API_SECURITY,
        action="api_key_revoked",
        entity_type="api_key",
        entity_id=key_id,
        user_id=revoked_by,
    )
    return True


def store_provider_secret(
    db: Session,
    *,
    provider_code: str,
    secret_name: str,
    value: str,
    environment: ApiEnvironment,
) -> ProviderSecret:
    from app.services.credential_vault import store_credential

    return store_credential(
        db,
        provider_code=provider_code,
        secret_name=secret_name,
        value=value,
        environment=environment,
    )


def verify_request_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def log_security_event(
    db: Session,
    *,
    event_type: str,
    source_ip: str | None = None,
    path: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(
        SecurityMonitorEvent(
            event_type=event_type,
            source_ip=source_ip,
            path=path,
            details=details,
        )
    )


def list_api_keys(db: Session) -> list[ApiKey]:
    return db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()
