from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SendResult:
    success: bool
    provider_id: str | None = None
    message: str | None = None
    raw_response: dict | None = None


class EmailProvider(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str, *, html: bool = False) -> SendResult:
        pass


class SmsProvider(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        pass

    @abstractmethod
    def send_sms(self, to: str, message: str) -> SendResult:
        pass
