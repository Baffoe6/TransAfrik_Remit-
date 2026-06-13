"""Webhook processing framework for payment and remittance providers."""

import hashlib
import hmac
import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.enums import WebhookStatus
from app.models.webhook import ProviderConfig, WebhookEvent
from app.services.payment_webhook_service import apply_payment_webhook

logger = logging.getLogger(__name__)


def verify_signature(payload: bytes, signature: str | None, secret: str | None) -> bool:
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def record_webhook(
    db: Session,
    *,
    provider_code: str,
    event_type: str,
    payload: dict,
    external_id: str | None = None,
) -> WebhookEvent:
    event = WebhookEvent(
        provider_code=provider_code,
        event_type=event_type,
        external_id=external_id,
        payload=payload,
        status=WebhookStatus.RECEIVED,
    )
    db.add(event)
    db.flush()
    return event


def process_webhook(db: Session, event: WebhookEvent) -> WebhookEvent:
    """Route webhook to provider-specific handler."""
    handlers = {
        "pay_at": _handle_payment,
        "easy_pay": _handle_payment,
        "eft": _handle_payment,
        "mukuru_api": _handle_mukuru,
        "manual_mukuru": _handle_mukuru,
    }
    handler = handlers.get(event.provider_code, _handle_unknown)
    try:
        notes = handler(db, event)
        event.status = WebhookStatus.PROCESSED
        event.processing_notes = notes
    except Exception as e:
        logger.exception("Webhook processing failed: %s", event.id)
        event.status = WebhookStatus.FAILED
        event.processing_notes = str(e)
    event.processed_at = datetime.now(UTC)
    db.flush()
    return event


def _handle_payment(db: Session, event: WebhookEvent) -> str:
    result = apply_payment_webhook(db, event.provider_code, event.payload)
    if result.success:
        return f"{event.provider_code} payment webhook applied: {result.reference_number} -> {result.status}"
    return f"{event.provider_code} webhook logged (no state change)"


def _handle_mukuru(db: Session, event: WebhookEvent) -> str:
    ref = event.payload.get("reference") or event.payload.get("transfer_reference")
    status = event.payload.get("status", "unknown")
    return f"Mukuru webhook stub processed: {event.event_type} ref={ref} status={status}"


def _handle_unknown(db: Session, event: WebhookEvent) -> str:
    return f"No handler for provider {event.provider_code} — logged only"


def get_provider_config(db: Session, provider_code: str) -> ProviderConfig | None:
    return db.query(ProviderConfig).filter(ProviderConfig.provider_code == provider_code).first()
