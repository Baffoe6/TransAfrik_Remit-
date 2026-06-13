"""Device fingerprinting, trust, and login risk scoring."""

import hashlib
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.trusted_device import TrustedDevice

RISK_THRESHOLD_STEP_UP = 40
RISK_THRESHOLD_HIGH = 70


def fingerprint_device(device_id: str | None, user_agent: str | None) -> str:
    raw = f"{device_id or 'unknown'}:{user_agent or 'unknown'}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_trusted_device(db: Session, user_id: int, fingerprint: str) -> TrustedDevice | None:
    return (
        db.query(TrustedDevice)
        .filter(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_fingerprint_hash == fingerprint,
        )
        .first()
    )


def compute_login_risk(
    db: Session,
    *,
    user_id: int,
    fingerprint: str,
    ip_address: str | None,
    user_agent: str | None,
    otp_requests_recent: int = 0,
) -> dict:
    device = get_trusted_device(db, user_id, fingerprint)
    score = 0
    factors: list[str] = []

    if not device:
        score += 35
        factors.append("new_device")
    elif not device.is_trusted:
        score += 20
        factors.append("untrusted_device")
    else:
        score -= 15
        factors.append("trusted_device")

    if device and ip_address and device.ip_address and device.ip_address != ip_address:
        score += 15
        factors.append("new_ip")

    if otp_requests_recent >= 3:
        score += 25
        factors.append("otp_velocity")

    if not user_agent:
        score += 10
        factors.append("missing_user_agent")

    score = max(0, min(100, score))
    requires_step_up = score >= RISK_THRESHOLD_STEP_UP and not (device and device.is_trusted)
    risk_level = "low" if score < 40 else "medium" if score < RISK_THRESHOLD_HIGH else "high"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "requires_step_up": requires_step_up,
        "factors": factors,
        "device_trusted": bool(device and device.is_trusted),
        "device_id": device.id if device else None,
    }


def record_device_login(
    db: Session,
    *,
    user_id: int,
    fingerprint: str,
    ip_address: str | None,
    user_agent: str | None,
    device_label: str | None,
    risk_score: int,
    trust_device: bool = False,
) -> TrustedDevice:
    device = get_trusted_device(db, user_id, fingerprint)
    now = datetime.now(UTC)
    if not device:
        device = TrustedDevice(
            user_id=user_id,
            device_fingerprint_hash=fingerprint,
            device_label=device_label,
            ip_address=ip_address,
            user_agent=user_agent,
            risk_score=risk_score,
            is_trusted=trust_device,
            trusted_at=now if trust_device else None,
            last_seen_at=now,
            login_count=1,
        )
        db.add(device)
    else:
        device.last_seen_at = now
        device.login_count += 1
        device.risk_score = risk_score
        device.ip_address = ip_address or device.ip_address
        device.user_agent = user_agent or device.user_agent
        if device_label:
            device.device_label = device_label
        if trust_device:
            device.is_trusted = True
            device.trusted_at = device.trusted_at or now
    db.flush()
    return device


def list_user_devices(db: Session, user_id: int) -> list[TrustedDevice]:
    return (
        db.query(TrustedDevice)
        .filter(TrustedDevice.user_id == user_id)
        .order_by(TrustedDevice.last_seen_at.desc().nullslast())
        .all()
    )


def set_device_trust(db: Session, user_id: int, device_id: int, trusted: bool) -> TrustedDevice | None:
    device = (
        db.query(TrustedDevice)
        .filter(TrustedDevice.id == device_id, TrustedDevice.user_id == user_id)
        .first()
    )
    if not device:
        return None
    device.is_trusted = trusted
    device.trusted_at = datetime.now(UTC) if trusted else None
    db.flush()
    return device
