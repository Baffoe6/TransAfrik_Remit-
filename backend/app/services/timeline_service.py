from sqlalchemy.orm import Session

from app.models.transfer import Transfer
from app.models.transfer_status_history import TransferStatusHistory
from app.models.transfer_tracking import TransferTrackingEvent
from app.services.transfer import TRANSFER_TIMELINE_LABELS, build_transfer_timeline


NEXT_STATUS_HINTS = {
    "draft": "awaiting_payment",
    "awaiting_payment": "payment_verified",
    "payment_pending_verification": "payment_verified",
    "payment_verified": "compliance_review",
    "compliance_review": "ready_for_processing",
    "ready_for_processing": "submitted_to_mukuru",
    "submitted_to_mukuru": "processing",
    "processing": "completed",
}


def emit_tracking_event(
    db: Session,
    *,
    transfer_id: int,
    event_type: str,
    label: str,
    status: str | None = None,
    message: str | None = None,
    event_metadata: dict | None = None,
) -> TransferTrackingEvent:
    event = TransferTrackingEvent(
        transfer_id=transfer_id,
        event_type=event_type,
        status=status,
        label=label,
        message=message,
        event_metadata=event_metadata,
    )
    db.add(event)
    db.flush()
    return event


def build_realtime_tracking(db: Session, transfer: Transfer) -> dict:
    history = (
        db.query(TransferStatusHistory)
        .filter(TransferStatusHistory.transfer_id == transfer.id)
        .order_by(TransferStatusHistory.created_at.asc())
        .all()
    )
    tracking_events = (
        db.query(TransferTrackingEvent)
        .filter(TransferTrackingEvent.transfer_id == transfer.id)
        .order_by(TransferTrackingEvent.created_at.asc())
        .all()
    )

    timeline = build_transfer_timeline(transfer, history)
    status_key = transfer.status.value if hasattr(transfer.status, "value") else str(transfer.status)
    next_status = NEXT_STATUS_HINTS.get(status_key)

    events = [
        {
            "id": e.id,
            "event_type": e.event_type,
            "status": e.status,
            "label": e.label,
            "message": e.message,
            "metadata": e.event_metadata,
            "timestamp": e.created_at.isoformat() if e.created_at else None,
        }
        for e in tracking_events
    ]

    return {
        "transfer_id": transfer.id,
        "reference": transfer.reference,
        "current_status": status_key,
        "current_label": TRANSFER_TIMELINE_LABELS.get(transfer.status, status_key),
        "next_expected_status": next_status,
        "next_expected_label": TRANSFER_TIMELINE_LABELS.get(next_status, next_status.replace("_", " ").title()) if next_status else None,
        "timeline": timeline,
        "events": events,
        "updated_at": transfer.updated_at.isoformat() if transfer.updated_at else None,
        "is_terminal": status_key in ("completed", "failed", "refunded", "expired"),
    }
