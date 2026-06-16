from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.webhooks.handler import get_provider_config, process_webhook, record_webhook
from app.webhooks.security import (
    FLUTTERWAVE_WEBHOOK_PROVIDERS,
    flutterwave_webhook_status_code,
    queue_webhook_for_processing,
    resolve_flutterwave_webhook_secret,
    secure_flutterwave_webhook_ingress,
    secure_webhook_ingress,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/{provider_code}")
async def receive_webhook(
    provider_code: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    x_signature: Annotated[str | None, Header()] = None,
    x_webhook_timestamp: Annotated[str | None, Header()] = None,
    x_webhook_nonce: Annotated[str | None, Header()] = None,
    verif_hash: Annotated[str | None, Header(alias="verif-hash")] = None,
):
    body = await request.body()
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    config = get_provider_config(db, provider_code)

    if provider_code in FLUTTERWAVE_WEBHOOK_PROVIDERS:
        secret = resolve_flutterwave_webhook_secret(config)
        ok, error, external_id = secure_flutterwave_webhook_ingress(
            db,
            provider_code=provider_code,
            payload=payload,
            verif_hash=verif_hash,
            secret=secret,
        )
    else:
        secret = config.webhook_secret if config else None
        ok, error, external_id = secure_webhook_ingress(
            db,
            provider_code=provider_code,
            body=body,
            payload=payload,
            signature=x_signature,
            secret=secret,
            timestamp_header=x_webhook_timestamp,
            nonce_header=x_webhook_nonce,
        )

    if not ok:
        if provider_code in FLUTTERWAVE_WEBHOOK_PROVIDERS:
            raise HTTPException(status_code=flutterwave_webhook_status_code(error), detail=error)
        status_code = status.HTTP_409_CONFLICT if error and "Duplicate" in error else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=status_code, detail=error)

    event_type = payload.get("event") or payload.get("event_type") or payload.get("type") or "unknown"
    event = record_webhook(
        db,
        provider_code=provider_code,
        event_type=event_type,
        payload=payload,
        external_id=external_id,
    )

    settings = get_settings()
    if settings.webhook_queue_enabled:
        queue_webhook_for_processing(provider_code, event.id, payload)

    process_webhook(db, event)
    db.commit()

    return {"received": True, "event_id": event.id, "status": event.status.value, "idempotent": True}
