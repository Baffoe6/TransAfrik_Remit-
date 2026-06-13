from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WhatsAppInboundMessage:
    from_number: str
    body: str
    message_id: str | None = None


@dataclass
class WhatsAppOutboundMessage:
    to_number: str
    body: str


@dataclass
class WhatsAppSendResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class WhatsAppBotTransport(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def send_message(self, message: WhatsAppOutboundMessage) -> WhatsAppSendResult:
        pass

    def parse_webhook(self, payload: dict) -> WhatsAppInboundMessage | None:
        return None
