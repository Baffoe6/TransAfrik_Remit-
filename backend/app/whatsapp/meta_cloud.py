import logging

from app.whatsapp.base import WhatsAppBotTransport, WhatsAppInboundMessage, WhatsAppOutboundMessage, WhatsAppSendResult

logger = logging.getLogger(__name__)


class MetaCloudWhatsAppTransport(WhatsAppBotTransport):
    def __init__(self, access_token: str | None = None, phone_number_id: str | None = None):
        self.access_token = access_token
        self.phone_number_id = phone_number_id

    @property
    def provider_code(self) -> str:
        return "meta_cloud"

    def send_message(self, message: WhatsAppOutboundMessage) -> WhatsAppSendResult:
        logger.info("[Meta Cloud WhatsApp -> %s] %s", message.to_number, message.body[:200])
        return WhatsAppSendResult(success=True, provider_message_id="meta-console")

    def parse_webhook(self, payload: dict) -> WhatsAppInboundMessage | None:
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None
            msg = messages[0]
            return WhatsAppInboundMessage(
                from_number=msg.get("from", ""),
                body=msg.get("text", {}).get("body", ""),
                message_id=msg.get("id"),
            )
        except (IndexError, KeyError, TypeError):
            return None
