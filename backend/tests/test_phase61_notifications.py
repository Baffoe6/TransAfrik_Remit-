"""Phase 6.1: notification provider registry tests."""

from app.notifications.registry import get_email_provider, get_sms_provider, get_whatsapp_provider


def test_email_providers_instantiate():
    for code in ("smtp", "sendgrid", "ses"):
        provider = get_email_provider(code)
        assert provider.provider_code == code


def test_sms_providers_instantiate():
    for code in ("console", "africas_talking", "twilio"):
        provider = get_sms_provider(code)
        assert provider.provider_code == code


def test_whatsapp_providers_instantiate():
    for code in ("console", "twilio"):
        provider = get_whatsapp_provider(code)
        assert provider.provider_code in ("console_whatsapp", "twilio_whatsapp")
