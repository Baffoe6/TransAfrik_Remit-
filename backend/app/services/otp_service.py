"""OTP generation, delivery (SMS/WhatsApp), and verification."""

import logging
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.notifications.registry import get_sms_provider, get_whatsapp_provider
from app.redis.otp_store import check_otp_rate_limit, delete_otp, store_otp, verify_otp
from app.utils.phone import validate_phone_number

logger = logging.getLogger(__name__)

OTP_PURPOSE_LOGIN = "login"
OTP_PURPOSE_VERIFY_PHONE = "verify_phone"
OTP_PURPOSE_STEP_UP = "step_up"
OTP_PURPOSE_PASSWORD_RESET = "password_reset"
OTP_PURPOSE_PIN_RESET = "pin_reset"
OTP_PURPOSE_BENEFICIARY_CHANGE = "beneficiary_change"
OTP_PURPOSE_HIGH_VALUE_TRANSFER = "high_value_transfer"
OTP_PURPOSE_KYC_UPDATE = "kyc_update"

VALID_CHANNELS = ("sms", "whatsapp")
VALID_PURPOSES = (
    OTP_PURPOSE_LOGIN,
    OTP_PURPOSE_VERIFY_PHONE,
    OTP_PURPOSE_STEP_UP,
    OTP_PURPOSE_PASSWORD_RESET,
    OTP_PURPOSE_PIN_RESET,
    OTP_PURPOSE_BENEFICIARY_CHANGE,
    OTP_PURPOSE_HIGH_VALUE_TRANSFER,
    OTP_PURPOSE_KYC_UPDATE,
)


def generate_otp_code(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


def _otp_message(code: str, purpose: str) -> str:
    if purpose == OTP_PURPOSE_VERIFY_PHONE:
        return f"Your TransAfrik Remit verification code is {code}. Valid for 10 minutes. Do not share this code."
    if purpose == OTP_PURPOSE_PIN_RESET:
        return f"Your TransAfrik Remit PIN reset code is {code}. Valid for 10 minutes. Do not share this code."
    return f"Your TransAfrik Remit login code is {code}. Valid for 10 minutes. Do not share this code."


def send_otp(
    *,
    mobile: str,
    channel: str,
    purpose: str,
    user_id: int | None = None,
) -> dict:
    if channel not in VALID_CHANNELS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Channel must be sms or whatsapp")
    if purpose not in VALID_PURPOSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP purpose")

    normalized = validate_phone_number(mobile)
    if not check_otp_rate_limit(normalized):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Try again later.",
        )

    settings = get_settings()
    if settings.otp_provider == "twilio_verify":
        from app.services.twilio_verify_service import send_verification

        twilio_result = send_verification(normalized, channel)
        if twilio_result.get("sent"):
            logger.info(
                "Twilio Verify OTP purpose=%s channel=%s mobile=%s",
                purpose,
                channel,
                normalized[-4:],
            )
            return {
                "sent": True,
                "channel": channel,
                "purpose": purpose,
                "mobile_number": normalized,
                "provider": "twilio_verify",
                "expires_in_seconds": 600,
                "message": f"Verification code sent via {channel.upper()}",
            }

    code = generate_otp_code()
    store_otp(purpose, normalized, code, metadata={"channel": channel, "user_id": user_id})

    message = _otp_message(code, purpose)

    if channel == "sms":
        provider = get_sms_provider(settings.sms_provider)
        result = provider.send_sms(normalized, message)
    else:
        provider = get_whatsapp_provider(settings.whatsapp_provider)
        result = provider.send_message(normalized, message)

    if not result.success:
        delete_otp(purpose, normalized)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Failed to send OTP: {result.message}")

    logger.info("OTP sent purpose=%s channel=%s mobile=%s provider=%s", purpose, channel, normalized[-4:], provider.provider_code)

    response: dict = {
        "sent": True,
        "channel": channel,
        "purpose": purpose,
        "mobile_number": normalized,
        "expires_in_seconds": 600,
        "message": f"Verification code sent via {channel.upper()}",
    }
    if settings.environment.lower() in ("development", "test") and settings.otp_dev_expose_code:
        response["dev_code"] = code
    return response


def verify_otp_code(mobile: str, purpose: str, code: str) -> str:
    normalized = validate_phone_number(mobile)
    settings = get_settings()
    if settings.otp_provider == "twilio_verify":
        from app.services.twilio_verify_service import check_verification

        if check_verification(normalized, code):
            return normalized
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code")
    if not verify_otp(purpose, normalized, code.strip()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code")
    return normalized


def find_user_by_mobile(db: Session, mobile: str) -> User | None:
    normalized = validate_phone_number(mobile)
    return db.query(User).filter(User.mobile_number == normalized).first()
