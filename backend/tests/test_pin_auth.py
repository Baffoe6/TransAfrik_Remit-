"""PIN authentication — schema validation and security helpers."""

import pytest

from app.schemas.auth import PinLoginRequest, PinResetConfirm, RegisterRequest
from app.utils.security import hash_pin, verify_pin


def test_hash_pin_never_stores_plaintext():
    pin = "4829"
    hashed = hash_pin(pin)
    assert hashed != pin
    assert verify_pin(pin, hashed)
    assert not verify_pin("0000", hashed)


def test_register_request_requires_pin_and_consents():
    req = RegisterRequest(
        mobile_number="+27821234567",
        first_name="Thabo",
        last_name="Molefe",
        pin="1234",
        accept_popia=True,
        accept_terms=True,
    )
    assert req.pin == "1234"
    assert req.email is None


def test_register_request_rejects_invalid_pin():
    with pytest.raises(ValueError):
        RegisterRequest(
            mobile_number="+27821234567",
            first_name="A",
            last_name="B",
            pin="12ab",
            accept_popia=True,
            accept_terms=True,
        )


def test_register_request_email_optional():
    req = RegisterRequest(
        mobile_number="+27821234567",
        first_name="A",
        last_name="B",
        pin="5678",
        accept_popia=True,
        accept_terms=True,
    )
    assert req.email is None


def test_pin_login_request_normalizes_mobile():
    req = PinLoginRequest(mobile_number="0821234567", pin="1234")
    assert req.mobile_number.startswith("+")


def test_pin_reset_confirm():
    req = PinResetConfirm(mobile_number="+27821234567", code="654321", new_pin="9876")
    assert req.new_pin == "9876"


@pytest.mark.skipif(
    "postgresql" not in __import__("os").environ.get("DATABASE_URL", ""),
    reason="Integration tests require PostgreSQL",
)
def test_pin_register_and_login_integration():
    import secrets

    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    mobile = "+2782" + "".join(secrets.choice("0123456789") for _ in range(7))

    reg = client.post(
        "/api/v1/auth/register",
        json={
            "mobile_number": mobile,
            "first_name": "Pin",
            "last_name": "Test",
            "pin": "4321",
            "accept_popia": True,
            "accept_terms": True,
        },
    )
    assert reg.status_code == 201, reg.text
    assert reg.json().get("access_token")

    login = client.post("/api/v1/auth/login/pin", json={"mobile_number": mobile, "pin": "4321"})
    assert login.status_code == 200, login.text
    assert login.json().get("access_token")

