"""Phase 6.1: credential vault encryption tests."""

import os

import pytest

from app.models.enums import ApiEnvironment
from app.services.credential_vault import get_credential_value, list_credentials, store_credential
from app.vault.encryption import decrypt_value, encrypt_value


def test_fernet_roundtrip():
    original = "sk_live_test_secret_12345"
    encrypted = encrypt_value(original)
    assert encrypted != original
    assert decrypt_value(encrypted) == original


@pytest.mark.skipif(
    "postgresql" not in os.environ.get("DATABASE_URL", ""),
    reason="Vault DB tests require PostgreSQL",
)
def test_vault_store_and_list():
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        record = store_credential(
            db,
            provider_code="pay_at",
            secret_name="api_key_test",
            value="test-api-key-value",
            environment=ApiEnvironment.DEVELOPMENT,
        )
        db.commit()
        assert get_credential_value(record) == "test-api-key-value"
        listed = list_credentials(db, provider_code="pay_at")
        assert any(item["secret_name"] == "api_key_test" for item in listed)
    finally:
        db.close()
