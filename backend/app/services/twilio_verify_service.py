"""Twilio Verify integration — SMS OTP (Phase 1), WhatsApp (Phase 2)."""

import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


def is_twilio_verify_enabled() -> bool:
    s = get_settings()
    return bool(s.twilio_verify_service_sid and s.twilio_account_sid and s.twilio_auth_token)


def send_verification(mobile: str, channel: str = "sms") -> dict:
    """Start a Twilio Verify check. Falls back to console OTP when not configured."""
    settings = get_settings()
    if not is_twilio_verify_enabled():
        return {"provider": "console", "sent": False, "fallback": True}

    try:
        from twilio.rest import Client  # noqa: PLC0415
    except ModuleNotFoundError:
        logger.error("twilio package not installed — add 'twilio>=9.0.0' to requirements.txt")
        return {"provider": "console", "sent": False, "fallback": True, "error": "twilio_not_installed"}

    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        verification = client.verify.v2.services(settings.twilio_verify_service_sid).verifications.create(
            to=mobile,
            channel="whatsapp" if channel == "whatsapp" else "sms",
        )
        logger.info("Twilio Verify sent status=%s to=%s", verification.status, mobile[-4:])
        return {"provider": "twilio_verify", "sent": True, "status": verification.status}
    except Exception as exc:
        logger.exception("Twilio Verify send failed — falling back to app OTP")
        return {"provider": "console", "sent": False, "fallback": True, "error": str(exc)}


def check_verification(mobile: str, code: str) -> bool:
    settings = get_settings()
    if not is_twilio_verify_enabled():
        return False

    try:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        result = client.verify.v2.services(settings.twilio_verify_service_sid).verification_checks.create(
            to=mobile,
            code=code.strip(),
        )
        return result.status == "approved"
    except Exception:
        logger.exception("Twilio Verify check failed")
        return False
