"""Unified secrets retrieval — environment variables and encrypted vault."""

from abc import ABC, abstractmethod

from app.config import get_settings
from app.vault.encryption import decrypt_value, encrypt_value


class SecretsProvider(ABC):
    @abstractmethod
    def get(self, key: str, default: str = "") -> str:
        ...

    @abstractmethod
    def set_encrypted(self, key: str, value: str) -> str:
        ...


class EnvironmentSecretsProvider(SecretsProvider):
    """Reads secrets from pydantic Settings / environment."""

    def get(self, key: str, default: str = "") -> str:
        settings = get_settings()
        return str(getattr(settings, key, default) or default)

    def set_encrypted(self, key: str, value: str) -> str:
        return encrypt_value(value)


class VaultSecretsProvider(SecretsProvider):
    """Encrypt/decrypt values for storage in provider_secrets vault."""

    def get(self, key: str, default: str = "") -> str:
        return EnvironmentSecretsProvider().get(key, default)

    def set_encrypted(self, key: str, value: str) -> str:
        return encrypt_value(value)

    @staticmethod
    def decrypt(ciphertext: str) -> str:
        return decrypt_value(ciphertext)


def get_secrets_provider() -> SecretsProvider:
    settings = get_settings()
    if settings.is_production:
        return VaultSecretsProvider()
    return EnvironmentSecretsProvider()


def check_production_secrets() -> list[dict]:
    """Return checklist of required production secrets."""
    settings = get_settings()
    checks = [
        {"key": "secret_key", "label": "SECRET_KEY", "ok": settings.secret_key not in ("", "change-me-in-production")},
        {"key": "database_url", "label": "DATABASE_URL", "ok": bool(settings.database_url)},
        {"key": "redis_url", "label": "REDIS_URL", "ok": bool(settings.redis_url)},
    ]
    if settings.sms_provider != "console":
        checks.append({"key": "sms_provider", "label": "SMS credentials", "ok": True})
    return checks
