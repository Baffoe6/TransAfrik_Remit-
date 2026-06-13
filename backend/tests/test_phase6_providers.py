"""Provider credential validation tests."""

from unittest.mock import MagicMock

from app.services.provider_credential_service import simulate_webhook_url, verify_signature_hmac


def test_webhook_test_simulation():
    result = simulate_webhook_url("pay_at", "https://api.transafrik.co.za/webhooks/pay_at", "secret123")
    assert result["test_payload_sent"] is True
    assert result["signature_generated"] is True


def test_signature_verification_valid():
    import hashlib, hmac
    secret = "testsecret"
    payload = '{"event":"test"}'
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    result = verify_signature_hmac(secret, payload, sig)
    assert result["valid"] is True


def test_signature_verification_invalid():
    result = verify_signature_hmac("secret", "payload", "invalid")
    assert result["valid"] is False
