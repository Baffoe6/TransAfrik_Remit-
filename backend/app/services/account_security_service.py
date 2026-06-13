"""Account lockout, password rotation, and staff security policies."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.enums import SecurityEventType, UserRole
from app.models.security_hardening import PasswordHistory, SecurityAlert
from app.models.user import User
from app.services.security_service import log_security_event
from app.utils.security import verify_password

settings = get_settings()

STAFF_ROLES = frozenset(
    {UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER}
)


def is_staff_user(user: User) -> bool:
    return user.role in STAFF_ROLES


def is_account_locked(user: User) -> bool:
    if user.locked_until and user.locked_until > datetime.now(UTC):
        return True
    if user.locked_until and user.locked_until <= datetime.now(UTC):
        user.locked_until = None
        user.failed_login_attempts = 0
    return False


def record_failed_login(db: Session, user: User | None, ip: str | None, identifier: str) -> None:
    if not user:
        return
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= settings.account_lockout_max_attempts:
        user.locked_until = datetime.now(UTC) + timedelta(minutes=settings.account_lockout_minutes)
        log_security_event(
            db,
            event_type=SecurityEventType.ACCOUNT_LOCKED,
            user_id=user.id,
            ip_address=ip,
            details=f"Locked after {user.failed_login_attempts} failed attempts",
        )
        _create_alert(
            db,
            alert_type="account_locked",
            severity="high",
            user_id=user.id,
            ip_address=ip,
            title=f"Account locked: user #{user.id}",
            details=f"Identifier: {identifier}",
        )


def record_successful_login(db: Session, user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None


def password_is_expired(user: User) -> bool:
    if not is_staff_user(user):
        return False
    if user.must_change_password:
        return True
    if not user.password_changed_at:
        return get_settings().is_production
    age = datetime.now(UTC) - user.password_changed_at.replace(tzinfo=UTC)
    return age.days >= settings.password_max_age_days


def record_password_change(db: Session, user: User, new_password_hash: str) -> None:
    db.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))
    user.password_hash = new_password_hash
    user.password_changed_at = datetime.now(UTC)
    user.must_change_password = False
    # Keep last 5 hashes
    old = (
        db.query(PasswordHistory)
        .filter(PasswordHistory.user_id == user.id)
        .order_by(PasswordHistory.created_at.desc())
        .offset(5)
        .all()
    )
    for row in old:
        db.delete(row)


def password_was_used_recently(db: Session, user: User, plain_password: str) -> bool:
    if verify_password(plain_password, user.password_hash):
        return True
    history = (
        db.query(PasswordHistory)
        .filter(PasswordHistory.user_id == user.id)
        .order_by(PasswordHistory.created_at.desc())
        .limit(5)
        .all()
    )
    return any(verify_password(plain_password, h.password_hash) for h in history)


def _create_alert(
    db: Session,
    *,
    alert_type: str,
    severity: str,
    title: str,
    user_id: int | None = None,
    ip_address: str | None = None,
    details: str | None = None,
) -> SecurityAlert:
    alert = SecurityAlert(
        alert_type=alert_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        title=title,
        details=details,
    )
    db.add(alert)
    db.flush()
    return alert
