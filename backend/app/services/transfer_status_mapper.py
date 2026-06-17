"""Map internal transfer statuses to customer-facing MVP statuses."""

from app.models.enums import TransferStatus

MVP_STATUS_MAP: dict[TransferStatus, str] = {
    TransferStatus.QUOTE_CREATED: "DRAFT",
    TransferStatus.DRAFT: "DRAFT",
    TransferStatus.AWAITING_PAYMENT: "SUBMITTED",
    TransferStatus.PAYMENT_PENDING: "SUBMITTED",
    TransferStatus.CHECKOUT_CREATED: "SUBMITTED",
    TransferStatus.PAYMENT_PENDING_VERIFICATION: "SUBMITTED",
    TransferStatus.PAYMENT_VERIFIED: "FUNDS_RECEIVED",
    TransferStatus.COMPLIANCE_REVIEW: "UNDER_REVIEW",
    TransferStatus.READY_FOR_PROCESSING: "UNDER_REVIEW",
    TransferStatus.SUBMITTED_TO_MUKURU: "PROCESSING",
    TransferStatus.PROCESSING: "PROCESSING",
    TransferStatus.COMPLETED: "COMPLETED",
    TransferStatus.FAILED: "FAILED",
    TransferStatus.REFUNDED: "CANCELLED",
    TransferStatus.CANCELLED: "CANCELLED",
    TransferStatus.EXPIRED: "CANCELLED",
}


def to_mvp_status(status: TransferStatus | str) -> str:
    if isinstance(status, str):
        try:
            status = TransferStatus(status)
        except ValueError:
            return status.upper()
    return MVP_STATUS_MAP.get(status, status.value.upper())
