"""Tests for OTP auth, device trust, and risk scoring."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.device_trust_service import compute_login_risk, fingerprint_device
from app.services.otp_service import generate_otp_code, send_otp
from app.redis.otp_store import store_otp, verify_otp

client = TestClient(app)


def test_generate_otp_code_length():
    code = generate_otp_code()
    assert len(code) == 6
    assert code.isdigit()


def test_fingerprint_device_stable():
    fp1 = fingerprint_device("device-abc", "Mozilla/5.0")
    fp2 = fingerprint_device("device-abc", "Mozilla/5.0")
    assert fp1 == fp2
    assert fp1 != fingerprint_device("device-xyz", "Mozilla/5.0")


def test_compute_login_risk_new_device():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    risk = compute_login_risk(db, user_id=1, fingerprint="abc", ip_address="1.2.3.4", user_agent="ua")
    assert risk["risk_score"] >= 30
    assert "new_device" in risk["factors"]


def test_otp_store_verify_consume():
    store_otp("login", "+27721234567", "654321", ttl=60)
    assert verify_otp("login", "+27721234567", "654321") is True
    assert verify_otp("login", "+27721234567", "654321") is False


@patch("app.services.otp_service.get_sms_provider")
def test_send_otp_sms(mock_sms):
    mock_provider = MagicMock()
    mock_provider.provider_code = "console"
    mock_provider.send_sms.return_value = MagicMock(success=True, message="ok")
    mock_sms.return_value = mock_provider

    result = send_otp(mobile="+27721234567", channel="sms", purpose="login", user_id=1)
    assert result["sent"] is True
    assert result["channel"] == "sms"
    assert "dev_code" in result


@patch("app.services.otp_service.get_whatsapp_provider")
def test_send_otp_whatsapp(mock_wa):
    mock_provider = MagicMock()
    mock_provider.provider_code = "console_whatsapp"
    mock_provider.send_message.return_value = MagicMock(success=True, message="ok")
    mock_wa.return_value = mock_provider

    result = send_otp(mobile="+27721234567", channel="whatsapp", purpose="verify_phone", user_id=1)
    assert result["sent"] is True
    assert result["channel"] == "whatsapp"
