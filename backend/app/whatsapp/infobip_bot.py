import logging

from app.whatsapp.base import WhatsAppBotTransport, WhatsAppOutboundMessage, WhatsAppSendResult

logger = logging.getLogger(__name__)


class InfobipWhatsAppTransport(WhatsAppBotTransport):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url

    @property
    def provider_code(self) -> str:
        return "infobip"

    def send_message(self, message: WhatsAppOutboundMessage) -> WhatsAppSendResult:
        logger.info("[Infobip WhatsApp -> %s] %s", message.to_number, message.body[:200])
        return WhatsAppSendResult(success=True, provider_message_id="infobip-console")
