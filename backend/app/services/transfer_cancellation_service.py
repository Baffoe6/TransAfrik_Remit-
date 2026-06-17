"""Customer and automatic cancellation of unpaid transfers."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.enums import CancellationReason, PaymentEventType, PaymentReferenceStatus, TransferStatus
from app.models.payment_reference import PaymentReference
from app.models.security_hardening import SecurityAlert
from app.models.transfer import Transfer
from app.services.payment_collection import log_payment_event
from app.services.transfer import record_status_change

logger = logging.getLogger(__name__)

UNPAID_CANCELLABLE_STATUSES: frozenset[TransferStatus] = frozenset({
    TransferStatus.QUOTE_CREATED,
    TransferStatus.DRAFT,
    TransferStatus.AWAITING_PAYMENT,
    TransferStatus.PAYMENT_PENDING,
    TransferStatus.CHECKOUT_CREATED,
})

NON_CANCELLABLE_STATUSES: frozenset[TransferStatus] = frozenset({
    TransferStatus.PAYMENT_PENDING_VERIFICATION,
    TransferStatus.PAYMENT_VERIFIED,
    TransferStatus.COMPLIANCE_REVIEW,
    TransferStatus.READY_FOR_PROCESSING,
    TransferStatus.SUBMITTED_TO_MUKURU,
    TransferStatus.PROCESSING,
    TransferStatus.PAYOUT_PENDING,
    TransferStatus.COMPLETED,
    TransferStatus.FAILED,
    TransferStatus.REFUNDED,
    TransferStatus.CANCELLED,
})

UNPAID_EXPIRY_HOURS = 24
JOB_INTERVAL_MINUTES = 15


def is_unpaid_cancellable(status: TransferStatus | str) -> bool:
    if isinstance(status, str):
        try:
            status = TransferStatus(status)
        except ValueError:
            return False
    return status in UNPAID_CANCELLABLE_STATUSES


def can_customer_cancel(transfer: Transfer) -> bool:
    return is_unpaid_cancellable(transfer.status)


def _deactivate_payment_references(
    db: Session,
    transfer: Transfer,
    *,
    ref_status: PaymentReferenceStatus = PaymentReferenceStatus.CANCELLED,
) -> int:
    refs = (
        db.query(PaymentReference)
        .filter(
            PaymentReference.transfer_id == transfer.id,
            PaymentReference.status.in_([
                PaymentReferenceStatus.DRAFT,
                PaymentReferenceStatus.AWAITING_PAYMENT,
            ]),
        )
        .all()
    )
    for ref in refs:
        ref.status = ref_status
    return len(refs)


def cancel_transfer(
    db: Session,
    transfer: Transfer,
    reason: CancellationReason,
    *,
    changed_by: int | None = None,
    notes: str | None = None,
) -> Transfer:
    """Idempotent cancellation of an unpaid transfer."""
    if transfer.status == TransferStatus.CANCELLED:
        return transfer

    if not is_unpaid_cancellable(transfer.status):
        raise ValueError(f"Transfer cannot be cancelled in status {transfer.status}")

    now = datetime.now(UTC)
    _deactivate_payment_references(db, transfer)
    transfer.cancelled_at = now
    transfer.cancellation_reason = reason.value

    record_status_change(
        db,
        transfer,
        TransferStatus.CANCELLED,
        changed_by=changed_by,
        notes=notes or reason.value,
        notify=False,
    )
    try:
        from app.services.transfer_notification_service import TransferNotificationService

        event = "cancelled_auto_24h" if reason == CancellationReason.EXPIRED_UNPAID_24H else "cancelled_customer"
        TransferNotificationService.notify_transfer_event(db, transfer, event)
    except Exception:
        logger.exception("Failed to send cancellation notification for transfer %s", transfer.id)
    log_payment_event(
        db,
        transfer.id,
        PaymentEventType.REFERENCE_EXPIRED,
        notes=f"Transfer cancelled: {reason.value}",
    )
    return transfer


def cancel_expired_unpaid_transfers(db: Session, *, now: datetime | None = None) -> int:
    """Cancel unpaid transfers older than 24 hours. Idempotent."""
    now = now or datetime.now(UTC)
    cutoff = now - timedelta(hours=UNPAID_EXPIRY_HOURS)

    candidates = (
        db.query(Transfer)
        .filter(
            Transfer.status.in_(list(UNPAID_CANCELLABLE_STATUSES)),
            Transfer.created_at <= cutoff,
        )
        .all()
    )

    cancelled = 0
    for transfer in candidates:
        if transfer.status == TransferStatus.CANCELLED:
            continue
        try:
            cancel_transfer(
                db,
                transfer,
                CancellationReason.EXPIRED_UNPAID_24H,
                notes="Automatically cancelled — payment not received within 24 hours",
            )
            cancelled += 1
        except ValueError:
            logger.warning("Skipped auto-cancel for transfer %s in status %s", transfer.id, transfer.status)
    return cancelled


def handle_late_payment_on_cancelled_transfer(
    db: Session,
    transfer: Transfer,
    payment_ref: PaymentReference,
    *,
    provider_code: str,
    payload: dict,
) -> None:
    """Record late payment evidence without advancing a cancelled transfer."""
    payment_ref.status = PaymentReferenceStatus.LATE_PAYMENT_RECEIVED
    transfer.cancellation_reason = CancellationReason.LATE_PAYMENT_RECEIVED.value

    log_payment_event(
        db,
        transfer.id,
        PaymentEventType.WEBHOOK_RECEIVED,
        provider_reference=payment_ref.reference_number,
        raw_payload=payload,
        notes=f"Late payment received after cancellation via {provider_code}",
    )

    alert = SecurityAlert(
        alert_type="late_payment_after_cancellation",
        severity="high",
        user_id=transfer.user_id,
        title=f"Late payment on cancelled transfer {transfer.reference}",
        details=(
            f"Transfer {transfer.reference} (id={transfer.id}) was cancelled but received a "
            f"{provider_code} payment webhook for reference {payment_ref.reference_number}. "
            "Manual review required."
        ),
    )
    db.add(alert)
    db.flush()
    try:
        from app.services.transfer_notification_service import TransferNotificationService

        TransferNotificationService.notify_late_payment_review(db, transfer)
    except Exception:
        logger.exception("Failed to send late payment notification for transfer %s", transfer.id)
    logger.warning(
        "Late payment webhook for cancelled transfer %s ref %s",
        transfer.reference,
        payment_ref.reference_number,
    )


CANCELLATION_REASON_LABELS: dict[str, str] = {
    CancellationReason.CUSTOMER_CANCELLED.value: "Customer cancelled",
    CancellationReason.EXPIRED_UNPAID_24H.value: "Expired unpaid after 24 hours",
    CancellationReason.ADMIN_CANCELLED.value: "Admin cancelled",
    CancellationReason.LATE_PAYMENT_RECEIVED.value: "Late payment received after cancellation",
}
