"""Provider credential validation, webhook testing, health checks."""

import hashlib
import hmac
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.webhook import ProviderConfig
from app.providers.registry import get_provider
from app.payment_providers.registry import get_payment_provider
from app.services.operations_center_service import check_provider_health

PILOT_PROVIDERS = ("mock_mukuru", "live_mukuru", "mukuru_api", "flutterwave", "pay_at", "easy_pay", "veengu", "onafriq")


def validate_provider_credentials(db: Session, provider_code: str) -> dict:
    from app.services.credential_vault import get_provider_credentials

    config = db.query(ProviderConfig).filter(ProviderConfig.provider_code == provider_code).first()
    if not config:
        return {"valid": False, "message": "Provider not configured"}

    vault_creds = get_provider_credentials(db, provider_code)
    creds = dict(config.config or {})
    creds.update(vault_creds)
    has_api_url = bool(config.api_base_url)
    has_secret = bool(config.webhook_secret) or bool(creds.get("api_key")) or len(vault_creds) > 0

    if provider_code in ("pay_at", "easy_pay", "kazang", "flash", "shoprite", "pick_n_pay"):
        try:
            provider = get_payment_provider(provider_code, creds)
            return {
                "valid": True,
                "message": f"{provider.provider_code} adapter loaded",
                "mode": "sandbox" if config.is_sandbox else "production",
                "has_credentials": has_secret or config.is_sandbox,
            }
        except Exception as exc:
            return {"valid": False, "message": str(exc)}

    if provider_code in ("mock_mukuru", "live_mukuru", "mukuru_api", "flutterwave", "veengu", "onafriq"):
        try:
            if provider_code == "live_mukuru":
                from app.providers.mukuru.live_mukuru import LiveMukuruProvider
                p = LiveMukuruProvider(creds)
                valid = p.validate_credentials()
                return {"valid": valid, "message": "Live Mukuru credentials check", "mode": "production" if valid else "not_configured"}
            provider = get_provider(provider_code if provider_code != "live_mukuru" else "mock_mukuru")
            return {
                "valid": True,
                "message": f"{provider.provider_code} provider available",
                "mode": "sandbox" if config.is_sandbox else "production",
                "has_api_url": has_api_url,
            }
        except Exception as exc:
            return {"valid": False, "message": str(exc)}

    return {"valid": False, "message": "Unknown provider"}


def simulate_webhook_url(provider_code: str, webhook_url: str, secret: str | None = None) -> dict:
    payload = b'{"test": true, "provider": "' + provider_code.encode() + b'"}'
    signature = hmac.new((secret or "test").encode(), payload, hashlib.sha256).hexdigest() if secret else None
    return {
        "webhook_url": webhook_url,
        "test_payload_sent": True,
        "signature_generated": signature is not None,
        "signature_sample": signature[:16] + "..." if signature else None,
        "message": "Webhook test simulated (configure live endpoint for real delivery)",
        "tested_at": datetime.now(UTC).isoformat(),
    }


def verify_signature_hmac(secret: str, payload: str, signature: str) -> dict:
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {"valid": hmac.compare_digest(expected, signature), "expected_prefix": expected[:16]}


def run_provider_health_for_code(db: Session, provider_code: str) -> dict:
    checks = check_provider_health(db)
    match = next((c for c in checks if c.provider_code == provider_code), None)
    return {
        "provider_code": provider_code,
        "healthy": match.is_healthy if match else False,
        "latency_ms": match.latency_ms if match else None,
        "checked_at": match.checked_at.isoformat() if match else None,
    }
