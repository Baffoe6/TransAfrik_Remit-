"""Live webhook security: HMAC, replay protection, idempotency."""

import hashlib
import hmac
import time
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.webhook import ProviderConfig, WebhookEvent
from app.redis.client import get_redis
from app.redis.webhook_queue import enqueue_webhook

REPLAY_PREFIX = "wh:nonce:"
IDEMPOTENCY_PREFIX = "wh:idemp:"
DEFAULT_TOLERANCE_SECONDS = 300
FLUTTERWAVE_WEBHOOK_PROVIDERS = frozenset({"flutterwave", "card"})


def verify_hmac_signature(payload: bytes, signature: str | None, secret: str | None) -> bool:
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    provided = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


def resolve_flutterwave_webhook_secret(config: ProviderConfig | None = None) -> str | None:
    """Prefer FLUTTERWAVE_WEBHOOK_SECRET; fall back to provider config webhook_secret."""
    settings = get_settings()
    if settings.flutterwave_webhook_secret:
        return settings.flutterwave_webhook_secret
    if config and config.webhook_secret:
        return config.webhook_secret
    return None


def verify_flutterwave_verif_hash(verif_hash: str | None, secret: str | None) -> tuple[bool, str | None]:
    """Validate Flutterwave `verif-hash` header against the configured webhook secret."""
    if not secret:
        return False, "Flutterwave webhook secret not configured"
    if not verif_hash:
        return False, "Missing verif-hash header"
    if not hmac.compare_digest(verif_hash.strip(), secret.strip()):
        return False, "Invalid verif-hash"
    return True, None


def extract_flutterwave_external_id(payload: dict) -> str | None:
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("id", "flw_ref", "tx_ref"):
            value = data.get(key)
            if value is not None:
                return str(value)
    for key in ("id", "event_id"):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return None


def secure_flutterwave_webhook_ingress(
    db: Session,
    *,
    provider_code: str,
    payload: dict,
    verif_hash: str | None,
    secret: str | None,
) -> tuple[bool, str | None, str | None]:
    """Returns (ok, error_message, external_id)."""
    ok, err = verify_flutterwave_verif_hash(verif_hash, secret)
    if not ok:
        return False, err, None

    settings = get_settings()
    external_id = extract_flutterwave_external_id(payload)

    if settings.webhook_idempotency_enabled:
        ok, err = check_idempotency(db, provider_code, external_id)
        if not ok:
            return False, err, external_id

    return True, None, external_id


def flutterwave_webhook_status_code(error: str | None) -> int:
    if not error:
        return 200
    if error == "Missing verif-hash header" or error == "Flutterwave webhook secret not configured":
        return 401
    if error == "Invalid verif-hash":
        return 403
    if error and ("Duplicate" in error or "already processed" in error.lower()):
        return 409
    return 401


def check_timestamp_replay(timestamp_header: str | None, tolerance: int = DEFAULT_TOLERANCE_SECONDS) -> tuple[bool, str | None]:
    if not timestamp_header:
        return True, None
    try:
        ts = int(timestamp_header)
    except ValueError:
        return False, "Invalid timestamp header"
    now = int(time.time())
    if abs(now - ts) > tolerance:
        return False, "Webhook timestamp outside tolerance window"
    return True, None


def check_nonce_replay(nonce: str | None, ttl: int = DEFAULT_TOLERANCE_SECONDS) -> tuple[bool, str | None]:
    if not nonce:
        return True, None
    r = get_redis()
    key = f"{REPLAY_PREFIX}{nonce}"
    if r.exists(key):
        return False, "Duplicate webhook nonce (replay detected)"
    r.set(key, "1", ex=ttl, nx=True)
    return True, None


def check_idempotency(
    db: Session,
    provider_code: str,
    external_id: str | None,
    *,
    ttl: int = 86400,
) -> tuple[bool, str | None]:
    if not external_id:
        return True, None
    cache_key = f"{IDEMPOTENCY_PREFIX}{provider_code}:{external_id}"
    r = get_redis()
    if r.exists(cache_key):
        return False, f"Duplicate webhook external_id: {external_id}"
    existing = (
        db.query(WebhookEvent)
        .filter(
            WebhookEvent.provider_code == provider_code,
            WebhookEvent.external_id == external_id,
        )
        .first()
    )
    if existing:
        r.set(cache_key, "1", ex=ttl)
        return False, f"Webhook already processed: event #{existing.id}"
    r.set(cache_key, "1", ex=ttl, nx=True)
    return True, None


def secure_webhook_ingress(
    db: Session,
    *,
    provider_code: str,
    body: bytes,
    payload: dict,
    signature: str | None,
    secret: str | None,
    timestamp_header: str | None = None,
    nonce_header: str | None = None,
) -> tuple[bool, str | None, str | None]:
    """Returns (ok, error_message, external_id)."""
    settings = get_settings()
    if secret:
        if not verify_hmac_signature(body, signature, secret):
            return False, "Invalid webhook signature", None

    if settings.webhook_replay_protection:
        ok, err = check_timestamp_replay(timestamp_header)
        if not ok:
            return False, err, None
        ok, err = check_nonce_replay(nonce_header)
        if not ok:
            return False, err, None

    external_id = payload.get("id") or payload.get("reference") or payload.get("event_id")
    external_id = str(external_id) if external_id else None

    if settings.webhook_idempotency_enabled:
        ok, err = check_idempotency(db, provider_code, external_id)
        if not ok:
            return False, err, external_id

    return True, None, external_id


def queue_webhook_for_processing(provider_code: str, event_id: int, payload: dict) -> bool:
    return enqueue_webhook(provider_code, event_id, payload)
