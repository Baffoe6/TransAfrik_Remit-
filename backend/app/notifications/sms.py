"""SMS providers — Africa's Talking, Twilio, console fallback."""

import logging

import httpx

from app.config import get_settings
from app.notifications.base import SendResult, SmsProvider

logger = logging.getLogger(__name__)


class ConsoleSmsProvider(SmsProvider):
    @property
    def provider_code(self) -> str:
        return "console"

    def send_sms(self, to: str, message: str) -> SendResult:
        logger.info("SMS [%s] to=%s msg=%s", self.provider_code, to, message[:80])
        return SendResult(
            success=True,
            provider_id=f"stub-sms-{to[-4:]}",
            message="SMS logged (console)",
            raw_response={"mode": "stub", "to": to},
        )


class AfricasTalkingSmsProvider(SmsProvider):
    @property
    def provider_code(self) -> str:
        return "africas_talking"

    def send_sms(self, to: str, message: str) -> SendResult:
        settings = get_settings()
        if not settings.africas_talking_api_key or not settings.africas_talking_username:
            return ConsoleSmsProvider().send_sms(to, message)
        try:
            resp = httpx.post(
                "https://api.africastalking.com/version1/messaging",
                headers={"apiKey": settings.africas_talking_api_key, "Accept": "application/json"},
                data={
                    "username": settings.africas_talking_username,
                    "to": to,
                    "message": message,
                    "from": settings.africas_talking_sender_id or "TransAfrik",
                },
                timeout=30,
            )
            data = resp.json()
            recipients = data.get("SMSMessageData", {}).get("Recipients", [])
            if recipients and recipients[0].get("status") == "Success":
                return SendResult(success=True, provider_id=recipients[0].get("messageId"), message="Sent via Africa's Talking")
            return SendResult(success=False, message=str(data), raw_response=data)
        except Exception as exc:
            return SendResult(success=False, message=str(exc))


class TwilioSmsProvider(SmsProvider):
    @property
    def provider_code(self) -> str:
        return "twilio"

    def send_sms(self, to: str, message: str) -> SendResult:
        settings = get_settings()
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            return ConsoleSmsProvider().send_sms(to, message)
        try:
            from_number = settings.twilio_sms_from or settings.twilio_whatsapp_from
            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
            resp = httpx.post(
                url,
                auth=(settings.twilio_account_sid, settings.twilio_auth_token),
                data={"To": to, "From": from_number, "Body": message},
                timeout=30,
            )
            data = resp.json()
            if resp.status_code in (200, 201):
                return SendResult(success=True, provider_id=data.get("sid"), message="Sent via Twilio SMS")
            return SendResult(success=False, message=data.get("message", resp.text), raw_response=data)
        except Exception as exc:
            return SendResult(success=False, message=str(exc))
