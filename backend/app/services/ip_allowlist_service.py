"""Admin IP allowlist enforcement."""

import ipaddress

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.security_hardening import AdminIpAllowlist
from app.models.user import User
from app.services.account_security_service import is_staff_user

settings = get_settings()


def is_ip_allowed_for_admin(db: Session, user: User, ip: str | None) -> bool:
    if not is_staff_user(user):
        return True
    if not settings.admin_ip_allowlist_enabled:
        return True
    if not ip:
        return False

    entries = (
        db.query(AdminIpAllowlist)
        .filter(
            AdminIpAllowlist.is_active.is_(True),
            (AdminIpAllowlist.user_id == user.id) | (AdminIpAllowlist.user_id.is_(None)),
        )
        .all()
    )
    if not entries:
        return True  # enabled but empty = allow all until configured

    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False

    for entry in entries:
        try:
            if "/" in entry.ip_cidr:
                if addr in ipaddress.ip_network(entry.ip_cidr, strict=False):
                    return True
            elif addr == ipaddress.ip_address(entry.ip_cidr):
                return True
        except ValueError:
            continue
    return False


def list_allowlist(db: Session) -> list[AdminIpAllowlist]:
    return db.query(AdminIpAllowlist).order_by(AdminIpAllowlist.created_at.desc()).all()


def add_allowlist_entry(
    db: Session,
    *,
    ip_cidr: str,
    label: str | None,
    user_id: int | None,
    created_by: int,
) -> AdminIpAllowlist:
    entry = AdminIpAllowlist(
        ip_cidr=ip_cidr.strip(),
        label=label,
        user_id=user_id,
        created_by=created_by,
    )
    db.add(entry)
    db.flush()
    return entry
