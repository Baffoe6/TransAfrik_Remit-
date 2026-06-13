"""Fernet encryption for provider credential vault."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def _derive_fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_value(plaintext: str) -> str:
    settings = get_settings()
    fernet = Fernet(_derive_fernet_key(settings.secret_key))
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    settings = get_settings()
    fernet = Fernet(_derive_fernet_key(settings.secret_key))
    try:
        return fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt credential — wrong SECRET_KEY?") from exc
