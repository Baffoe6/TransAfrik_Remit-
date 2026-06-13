"""Login anomaly detection and security alert generation."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import SecurityEventType
from app.models.security import SecurityAuditLog
from app.models.security_hardening import SecurityAlert
from app.models.user import User
from app.services.security_service import log_security_event


def analyze_login_risk(
    db: Session,
    *,
    user: User,
    ip_address: str | None,
    risk_score: int,
    risk_factors: list[str],
) -> SecurityAlert | None:
    """Create alerts for high-risk logins and suspicious patterns."""
    alert = None

    if risk_score >= 70:
        alert = _create_alert(
            db,
            alert_type="high_risk_login",
            severity="high",
            user_id=user.id,
            ip_address=ip_address,
            title=f"High-risk login for user #{user.id}",
            details=f"score={risk_score} factors={risk_factors}",
        )
        log_security_event(
            db,
            event_type=SecurityEventType.LOGIN_ANOMALY,
            user_id=user.id,
            ip_address=ip_address,
            details=f"high_risk score={risk_score}",
        )

    if ip_address:
        failed_from_ip = _count_recent_events(db, SecurityEventType.LOGIN_FAILED, ip_address, minutes=15)
        if failed_from_ip >= 10:
            alert = _create_alert(
                db,
                alert_type="brute_force_ip",
                severity="critical",
                ip_address=ip_address,
                title=f"Brute-force pattern from {ip_address}",
                details=f"{failed_from_ip} failed logins in 15 minutes",
            )

    # Impossible travel placeholder: multiple countries in short window (IP-based heuristic)
    if "new_ip" in risk_factors and "untrusted_device" in risk_factors:
        _create_alert(
            db,
            alert_type="new_device_ip",
            severity="medium",
            user_id=user.id,
            ip_address=ip_address,
            title=f"New device + IP for user #{user.id}",
            details=str(risk_factors),
        )

    return alert


def get_failed_logins(db: Session, limit: int = 50) -> list[SecurityAuditLog]:
    return (
        db.query(SecurityAuditLog)
        .filter(SecurityAuditLog.event_type == SecurityEventType.LOGIN_FAILED)
        .order_by(SecurityAuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


def get_risk_events(db: Session, limit: int = 50) -> list[SecurityAuditLog]:
    types = [
        SecurityEventType.LOGIN_ANOMALY,
        SecurityEventType.STEP_UP_REQUIRED,
        SecurityEventType.MFA_FAILED,
        SecurityEventType.IP_BLOCKED,
        SecurityEventType.ACCOUNT_LOCKED,
    ]
    return (
        db.query(SecurityAuditLog)
        .filter(SecurityAuditLog.event_type.in_(types))
        .order_by(SecurityAuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


def get_unresolved_alerts(db: Session, limit: int = 50) -> list[SecurityAlert]:
    return (
        db.query(SecurityAlert)
        .filter(SecurityAlert.is_resolved.is_(False))
        .order_by(SecurityAlert.created_at.desc())
        .limit(limit)
        .all()
    )


def _count_recent_events(db: Session, event_type: SecurityEventType, ip: str, minutes: int) -> int:
    since = datetime.now(UTC) - timedelta(minutes=minutes)
    return (
        db.query(func.count(SecurityAuditLog.id))
        .filter(
            SecurityAuditLog.event_type == event_type,
            SecurityAuditLog.ip_address == ip,
            SecurityAuditLog.created_at >= since,
        )
        .scalar()
        or 0
    )


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
