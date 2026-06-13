import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import pyotp
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.enums import SecurityEventType
from app.models.security import SecurityAuditLog, UserMfa, UserSession

settings = get_settings()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def log_security_event(
    db: Session,
    *,
    event_type: SecurityEventType,
    user_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: str | None = None,
) -> SecurityAuditLog:
    entry = SecurityAuditLog(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )
    db.add(entry)
    db.flush()
    return entry


def create_session(
    db: Session,
    *,
    user_id: int,
    refresh_token: str,
    ip_address: str | None,
    user_agent: str | None,
) -> UserSession:
    session = UserSession(
        user_id=user_id,
        refresh_token_hash=hash_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    db.flush()
    return session


def validate_refresh_session(db: Session, refresh_token: str) -> UserSession | None:
    session = (
        db.query(UserSession)
        .filter(
            UserSession.refresh_token_hash == hash_token(refresh_token),
            UserSession.is_revoked.is_(False),
            UserSession.expires_at > datetime.now(UTC),
        )
        .first()
    )
    if session:
        session.last_used_at = datetime.now(UTC)
    return session


def revoke_session(db: Session, refresh_token: str) -> None:
    session = db.query(UserSession).filter(UserSession.refresh_token_hash == hash_token(refresh_token)).first()
    if session:
        session.is_revoked = True


def revoke_all_sessions(db: Session, user_id: int) -> int:
    count = (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.is_revoked.is_(False))
        .update({UserSession.is_revoked: True})
    )
    return count


def setup_mfa(db: Session, user_id: int) -> tuple[UserMfa, str]:
    secret = pyotp.random_base32()
    mfa = db.query(UserMfa).filter(UserMfa.user_id == user_id).first()
    if not mfa:
        mfa = UserMfa(user_id=user_id, totp_secret=secret)
        db.add(mfa)
    else:
        mfa.totp_secret = secret
        mfa.is_enabled = False
    db.flush()
    uri = pyotp.TOTP(secret).provisioning_uri(name=f"user-{user_id}", issuer_name="TransAfrik Remit")
    return mfa, uri


def verify_mfa_code(db: Session, user_id: int, code: str) -> bool:
    mfa = db.query(UserMfa).filter(UserMfa.user_id == user_id, UserMfa.is_enabled.is_(True)).first()
    if not mfa:
        return True
    totp = pyotp.TOTP(mfa.totp_secret)
    return totp.verify(code, valid_window=1)


def enable_mfa(db: Session, user_id: int, code: str) -> bool:
    mfa = db.query(UserMfa).filter(UserMfa.user_id == user_id).first()
    if not mfa:
        return False
    if not pyotp.TOTP(mfa.totp_secret).verify(code, valid_window=1):
        return False
    mfa.is_enabled = True
    mfa.enabled_at = datetime.now(UTC)
    mfa.backup_codes_hash = hashlib.sha256(secrets.token_hex(8).encode()).hexdigest()
    return True
