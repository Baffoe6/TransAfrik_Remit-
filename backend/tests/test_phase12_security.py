"""Phase 12 — production security hardening tests."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from app.config import get_settings
from app.models.enums import UserRole
from app.models.user import User
from app.services.account_security_service import (
    is_account_locked,
    is_staff_user,
    password_is_expired,
    record_failed_login,
)
from app.services.ip_allowlist_service import is_ip_allowed_for_admin
from app.secrets.provider import check_production_secrets, get_secrets_provider


def test_is_staff_user():
    admin = User(id=1, password_hash="x", role=UserRole.ADMIN)
    customer = User(id=2, password_hash="x", role=UserRole.CUSTOMER)
    assert is_staff_user(admin) is True
    assert is_staff_user(customer) is False


def test_account_lockout_detection():
    user = User(id=1, password_hash="x", role=UserRole.CUSTOMER, locked_until=datetime.now(UTC) + timedelta(minutes=10))
    assert is_account_locked(user) is True
    user.locked_until = datetime.now(UTC) - timedelta(minutes=1)
    assert is_account_locked(user) is False


def test_record_failed_login_locks_account():
    settings = get_settings()
    db = MagicMock()
    user = User(id=1, password_hash="x", role=UserRole.ADMIN, failed_login_attempts=settings.account_lockout_max_attempts - 1)
    record_failed_login(db, user, "1.2.3.4", "admin@test.com")
    assert user.failed_login_attempts == settings.account_lockout_max_attempts
    assert user.locked_until is not None


def test_password_expired_for_staff_without_change_date(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    user = User(id=1, password_hash="x", role=UserRole.ADMIN, password_changed_at=None)
    assert password_is_expired(user) is True
    get_settings.cache_clear()


def test_ip_allowlist_disabled_allows_all():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    user = User(id=1, password_hash="x", role=UserRole.ADMIN)
    assert is_ip_allowed_for_admin(db, user, "10.0.0.1") is True


def test_secrets_provider_returns_env():
    provider = get_secrets_provider()
    assert provider.get("environment", "development") in ("development", "production", "test")


def test_production_secrets_checklist():
    checks = check_production_secrets()
    keys = {c["key"] for c in checks}
    assert "secret_key" in keys
    assert "database_url" in keys


def test_security_center_dashboard_route():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    res = client.get("/api/v1/admin/security-center/dashboard")
    assert res.status_code in (401, 403)
