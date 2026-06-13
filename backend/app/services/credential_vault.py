"""Encrypted provider credential vault with sandbox/production switching."""

import enum
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.api_security import ProviderSecret
from app.models.enums import ApiEnvironment
from app.models.webhook import ProviderConfig
from app.vault.encryption import decrypt_value, encrypt_value

SANDBOX_ENVIRONMENTS = {ApiEnvironment.DEVELOPMENT, ApiEnvironment.STAGING}


def _enum_str(value) -> str:
    return value.value if isinstance(value, enum.Enum) else value


def _resolve_environment(config: ProviderConfig | None, override: ApiEnvironment | None) -> ApiEnvironment:
    if override:
        return override
    if config and config.is_sandbox:
        return ApiEnvironment.DEVELOPMENT
    return ApiEnvironment.PRODUCTION


def store_credential(
    db: Session,
    *,
    provider_code: str,
    secret_name: str,
    value: str,
    environment: ApiEnvironment,
    credential_type: str = "api_key",
) -> ProviderSecret:
    existing = (
        db.query(ProviderSecret)
        .filter(
            ProviderSecret.provider_code == provider_code,
            ProviderSecret.secret_name == secret_name,
            ProviderSecret.environment == environment,
        )
        .first()
    )
    ciphertext = encrypt_value(value)
    if existing:
        existing.encrypted_value = ciphertext
        existing.credential_type = credential_type
        existing.is_active = True
        existing.rotated_at = datetime.now(UTC)
        existing.validation_status = None
        record = existing
    else:
        record = ProviderSecret(
            provider_code=provider_code,
            secret_name=secret_name,
            encrypted_value=ciphertext,
            environment=environment,
            credential_type=credential_type,
            is_active=True,
            rotated_at=datetime.now(UTC),
        )
        db.add(record)
    db.flush()
    return record


def get_credential_value(record: ProviderSecret) -> str:
    return decrypt_value(record.encrypted_value)


def list_credentials(
    db: Session,
    provider_code: str | None = None,
    environment: ApiEnvironment | None = None,
) -> list[dict]:
    q = db.query(ProviderSecret).order_by(ProviderSecret.provider_code, ProviderSecret.secret_name)
    if provider_code:
        q = q.filter(ProviderSecret.provider_code == provider_code)
    if environment:
        q = q.filter(ProviderSecret.environment == environment)
    return [
        {
            "id": r.id,
            "provider_code": r.provider_code,
            "secret_name": r.secret_name,
            "environment": _enum_str(r.environment),
            "credential_type": r.credential_type,
            "is_active": r.is_active,
            "validation_status": r.validation_status,
            "last_validated_at": r.last_validated_at.isoformat() if r.last_validated_at else None,
            "rotated_at": r.rotated_at.isoformat() if r.rotated_at else None,
        }
        for r in q.all()
    ]


def get_provider_credentials(
    db: Session,
    provider_code: str,
    *,
    environment: ApiEnvironment | None = None,
) -> dict[str, str]:
    config = db.query(ProviderConfig).filter(ProviderConfig.provider_code == provider_code).first()
    env = _resolve_environment(config, environment)
    records = (
        db.query(ProviderSecret)
        .filter(
            ProviderSecret.provider_code == provider_code,
            ProviderSecret.environment == env,
            ProviderSecret.is_active.is_(True),
        )
        .all()
    )
    return {r.secret_name: get_credential_value(r) for r in records}


def validate_stored_credentials(db: Session, provider_code: str) -> dict:
    from app.services.provider_credential_service import validate_provider_credentials

    config = db.query(ProviderConfig).filter(ProviderConfig.provider_code == provider_code).first()
    creds = get_provider_credentials(db, provider_code)
    if config and creds:
        merged = dict(config.config or {})
        merged.update(creds)
        config.config = merged

    result = validate_provider_credentials(db, provider_code)
    now = datetime.now(UTC)
    env = _resolve_environment(config, None)
    for record in (
        db.query(ProviderSecret)
        .filter(ProviderSecret.provider_code == provider_code, ProviderSecret.environment == env)
        .all()
    ):
        record.last_validated_at = now
        record.validation_status = "valid" if result.get("valid") else "invalid"
    db.flush()
    result["environment"] = _enum_str(env)
    result["credential_count"] = len(creds)
    return result


def deactivate_credential(db: Session, credential_id: int) -> bool:
    record = db.query(ProviderSecret).filter(ProviderSecret.id == credential_id).first()
    if not record:
        return False
    record.is_active = False
    return True
