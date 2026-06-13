import logging

from app.whatsapp.base import WhatsAppBotTransport, WhatsAppOutboundMessage, WhatsAppSendResult

logger = logging.getLogger(__name__)


class TwilioWhatsAppBotTransport(WhatsAppBotTransport):
    def __init__(self, account_sid: str | None = None, auth_token: str | None = None, from_number: str | None = None):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    @property
    def provider_code(self) -> str:
        return "twilio"

    def send_message(self, message: WhatsAppOutboundMessage) -> WhatsAppSendResult:
        logger.info("[Twilio WhatsApp -> %s] %s", message.to_number, message.body[:200])
        return WhatsAppSendResult(success=True, provider_message_id="twilio-console")
