import logging

from sqlalchemy.orm import Session, joinedload

from app.models.enums import KycStatus, TransferStatus
from app.models.transfer import Transfer
from app.models.transfer_status_history import TransferStatusHistory
from app.models.user import User

logger = logging.getLogger(__name__)

STATUS_NOTIFICATION_EVENTS: dict[TransferStatus, str] = {
    TransferStatus.DRAFT: "transfer_created",
    TransferStatus.PAYMENT_PENDING_VERIFICATION: "payment_received",
    TransferStatus.PAYMENT_VERIFIED: "payment_verified",
    TransferStatus.COMPLIANCE_REVIEW: "compliance_review",
    TransferStatus.COMPLETED: "transfer_completed",
    TransferStatus.FAILED: "transfer_failed",
}


def record_status_change(
    db: Session,
    transfer: Transfer,
    new_status: TransferStatus,
    changed_by: int | None = None,
    notes: str | None = None,
    *,
    notify: bool = True,
) -> TransferStatusHistory:
    history = TransferStatusHistory(
        transfer_id=transfer.id,
        from_status=transfer.status,
        to_status=new_status,
        changed_by=changed_by,
        notes=notes,
    )
    transfer.status = new_status
    db.add(history)
    db.flush()

    try:
        from app.services.timeline_service import emit_tracking_event

        label = TRANSFER_TIMELINE_LABELS.get(new_status, new_status.value if hasattr(new_status, "value") else str(new_status))
        emit_tracking_event(
            db,
            transfer_id=transfer.id,
            event_type="status_change",
            status=new_status.value if hasattr(new_status, "value") else str(new_status),
            label=label,
            message=notes,
        )
    except Exception:
        logger.exception("Failed to emit tracking event for transfer %s", transfer.id)

    if notify and new_status in STATUS_NOTIFICATION_EVENTS:
        _send_lifecycle_notification(db, transfer, STATUS_NOTIFICATION_EVENTS[new_status])

    return history


def _send_lifecycle_notification(db: Session, transfer: Transfer, event: str) -> None:
    try:
        from app.notifications.service import notify_transfer_lifecycle

        loaded = (
            db.query(Transfer)
            .options(
                joinedload(Transfer.user).joinedload(User.profile),
                joinedload(Transfer.beneficiary),
                joinedload(Transfer.payment_references),
            )
            .filter(Transfer.id == transfer.id)
            .first()
        )
        if not loaded or not loaded.user:
            return
        notify_transfer_lifecycle(db, loaded, event, loaded.user)
    except Exception:
        logger.exception("Failed to send lifecycle notification for transfer %s", transfer.id)


def determine_initial_status(kyc_status: KycStatus) -> TransferStatus:
    if kyc_status != KycStatus.APPROVED:
        return TransferStatus.DRAFT
    return TransferStatus.DRAFT


TRANSFER_TIMELINE_LABELS = {
    TransferStatus.DRAFT: "Transfer Created",
    TransferStatus.AWAITING_PAYMENT: "Payment Generated",
    TransferStatus.PAYMENT_PENDING_VERIFICATION: "Payment Received",
    TransferStatus.PAYMENT_VERIFIED: "Payment Verified",
    TransferStatus.COMPLIANCE_REVIEW: "Compliance Review",
    TransferStatus.READY_FOR_PROCESSING: "Compliance Approved",
    TransferStatus.SUBMITTED_TO_MUKURU: "Submitted To Mukuru",
    TransferStatus.PROCESSING: "Processing",
    TransferStatus.COMPLETED: "Completed",
    TransferStatus.FAILED: "Failed",
    TransferStatus.REFUNDED: "Refunded",
    TransferStatus.EXPIRED: "Expired",
}


def build_transfer_timeline(transfer: Transfer, history: list[TransferStatusHistory]) -> list[dict]:
    seen: set[str] = set()
    timeline: list[dict] = []
    for h in history:
        status = h.to_status
        key = status.value if hasattr(status, "value") else str(status)
        if key in seen:
            continue
        seen.add(key)
        timeline.append({
            "status": key,
            "label": TRANSFER_TIMELINE_LABELS.get(status, key.replace("_", " ").title()),
            "timestamp": h.created_at.isoformat() if h.created_at else None,
            "notes": h.notes,
        })
    return timeline
