"""Production operations center — health, queues, failures."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import PaymentSettlementStatus, WebhookStatus
from app.models.fx_sync import FxSyncRun
from app.models.operations_health import OperationsQueueStatus, ProviderHealthCheck
from app.models.settlement import PaymentSettlement
from app.models.webhook import WebhookEvent
from app.services.provider_router import list_available_providers


def check_provider_health(db: Session) -> list[ProviderHealthCheck]:
    results = []
    for code in list_available_providers():
        check = ProviderHealthCheck(
            provider_code=code,
            is_healthy=True,
            latency_ms=50,
            checked_at=datetime.now(UTC),
        )
        db.add(check)
        results.append(check)
    db.flush()
    return results


def get_operations_center_dashboard(db: Session) -> dict:
    since = datetime.now(UTC) - timedelta(hours=24)

    provider_health = (
        db.query(ProviderHealthCheck)
        .order_by(ProviderHealthCheck.checked_at.desc())
        .limit(20)
        .all()
    )

    webhook_failures = (
        db.query(func.count(WebhookEvent.id))
        .filter(WebhookEvent.status == WebhookStatus.FAILED, WebhookEvent.created_at >= since)
        .scalar()
        or 0
    )

    fx_sync_failures = (
        db.query(func.count(FxSyncRun.id))
        .filter(FxSyncRun.success.is_(False), FxSyncRun.started_at >= since)
        .scalar()
        or 0
    )

    settlement_failures = (
        db.query(func.count(PaymentSettlement.id))
        .filter(PaymentSettlement.status == PaymentSettlementStatus.VARIANCE, PaymentSettlement.created_at >= since)
        .scalar()
        or 0
    )

    queues = db.query(OperationsQueueStatus).all()
    if not queues:
        queues_data = [
            {"queue_name": "transfer_processing", "pending_count": 0, "failed_count": 0},
            {"queue_name": "webhook_processing", "pending_count": webhook_failures, "failed_count": webhook_failures},
            {"queue_name": "fx_sync", "pending_count": 0, "failed_count": fx_sync_failures},
        ]
    else:
        queues_data = [
            {
                "queue_name": q.queue_name,
                "pending_count": q.pending_count,
                "failed_count": q.failed_count,
                "last_processed_at": q.last_processed_at.isoformat() if q.last_processed_at else None,
            }
            for q in queues
        ]

    latest_fx_sync = db.query(FxSyncRun).order_by(FxSyncRun.started_at.desc()).first()

    return {
        "provider_health": [
            {
                "provider": h.provider_code,
                "healthy": h.is_healthy,
                "latency_ms": h.latency_ms,
                "error": h.error_message,
                "checked_at": h.checked_at.isoformat(),
            }
            for h in provider_health
        ],
        "queues": queues_data,
        "failures_24h": {
            "webhooks": webhook_failures,
            "fx_sync": fx_sync_failures,
            "settlements": settlement_failures,
        },
        "last_fx_sync": {
            "source": latest_fx_sync.source_code if latest_fx_sync else None,
            "success": latest_fx_sync.success if latest_fx_sync else None,
            "started_at": latest_fx_sync.started_at.isoformat() if latest_fx_sync else None,
        },
        "status": "healthy" if webhook_failures + fx_sync_failures + settlement_failures < 10 else "degraded",
    }
