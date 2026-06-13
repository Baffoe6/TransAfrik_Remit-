import logging

import httpx

from app.config import get_settings
from app.notifications.base import SendResult

logger = logging.getLogger(__name__)


class WhatsAppProvider:
    @property
    def provider_code(self) -> str:
        raise NotImplementedError

    def send_message(self, to: str, message: str) -> SendResult:
        raise NotImplementedError


class ConsoleWhatsAppProvider(WhatsAppProvider):
    @property
    def provider_code(self) -> str:
        return "console_whatsapp"

    def send_message(self, to: str, message: str) -> SendResult:
        logger.info("[WhatsApp -> %s] %s", to, message[:200])
        return SendResult(success=True, provider_id="console", message="Logged to console", raw_response={"to": to})


class TwilioWhatsAppProvider(WhatsAppProvider):
    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_number: str | None = None,
    ):
        settings = get_settings()
        self.account_sid = account_sid or settings.twilio_account_sid
        self.auth_token = auth_token or settings.twilio_auth_token
        self.from_number = from_number or settings.twilio_whatsapp_from

    @property
    def provider_code(self) -> str:
        return "twilio_whatsapp"

    def send_message(self, to: str, message: str) -> SendResult:
        if not self.account_sid or not self.auth_token or not self.from_number:
            return ConsoleWhatsAppProvider().send_message(to, message)
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            resp = httpx.post(
                url,
                auth=(self.account_sid, self.auth_token),
                data={
                    "To": f"whatsapp:{to}" if not to.startswith("whatsapp:") else to,
                    "From": self.from_number,
                    "Body": message,
                },
                timeout=30,
            )
            data = resp.json()
            if resp.status_code in (200, 201):
                return SendResult(success=True, provider_id=data.get("sid"), message="Sent via Twilio WhatsApp")
            return SendResult(success=False, message=data.get("message", resp.text), raw_response=data)
        except Exception as exc:
            return SendResult(success=False, message=str(exc))
