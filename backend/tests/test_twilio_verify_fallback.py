"""Twilio Verify fallback behaviour."""

import builtins
import sys
from unittest.mock import MagicMock

import pytest

from app.services import twilio_verify_service as tvs


@pytest.fixture(autouse=True)
def twilio_credentials(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_VERIFY_SERVICE_SID", "VATEST")
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_send_verification_falls_back_when_twilio_package_missing(monkeypatch):
    monkeypatch.setattr(tvs, "is_twilio_verify_enabled", lambda: True)
    original_import = builtins.__import__

    def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "twilio" or name.startswith("twilio."):
            raise ModuleNotFoundError("No module named 'twilio'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_hook)
    result = tvs.send_verification("+27821234567", "sms")
    assert result["sent"] is False
    assert result.get("fallback") is True


def test_send_verification_falls_back_on_api_error(monkeypatch):
    monkeypatch.setattr(tvs, "is_twilio_verify_enabled", lambda: True)

    mock_client = MagicMock()
    mock_client.verify.v2.services.return_value.verifications.create.side_effect = RuntimeError("Twilio API down")
    mock_rest = MagicMock()
    mock_rest.Client.return_value = mock_client
    monkeypatch.setitem(sys.modules, "twilio", MagicMock(rest=mock_rest))
    monkeypatch.setitem(sys.modules, "twilio.rest", mock_rest)

    result = tvs.send_verification("+27821234567", "sms")
    assert result["sent"] is False
    assert result.get("fallback") is True
    assert "Twilio API down" in result.get("error", "")
