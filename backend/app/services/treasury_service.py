from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import PaymentReferenceStatus, TransferStatus
from app.models.payment_reference import PaymentReference
from app.models.transfer import Transfer


def get_treasury_dashboard(db: Session) -> dict:
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today_start.replace(day=1)

    funds_collected_today = db.query(func.coalesce(func.sum(PaymentReference.amount), 0)).filter(
        PaymentReference.status.in_([PaymentReferenceStatus.PAID, PaymentReferenceStatus.VERIFIED]),
        PaymentReference.updated_at >= today_start,
    ).scalar()

    funds_pending_processing = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.status.in_([
            TransferStatus.PAYMENT_VERIFIED,
            TransferStatus.COMPLIANCE_REVIEW,
            TransferStatus.READY_FOR_PROCESSING,
            TransferStatus.SUBMITTED_TO_MUKURU,
            TransferStatus.PROCESSING,
        ])
    ).scalar()

    funds_paid_out = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.status == TransferStatus.COMPLETED,
    ).scalar()

    outstanding_liabilities = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.status.in_([
            TransferStatus.READY_FOR_PROCESSING,
            TransferStatus.SUBMITTED_TO_MUKURU,
            TransferStatus.PROCESSING,
        ])
    ).scalar()

    revenue_today = db.query(func.coalesce(func.sum(Transfer.fee_zar), 0)).filter(
        Transfer.status == TransferStatus.COMPLETED,
        Transfer.completed_at >= today_start,
    ).scalar()

    revenue_month = db.query(func.coalesce(func.sum(Transfer.fee_zar), 0)).filter(
        Transfer.status == TransferStatus.COMPLETED,
        Transfer.completed_at >= month_start,
    ).scalar()

    awaiting_payment = db.query(func.coalesce(func.sum(Transfer.total_amount_zar), 0)).filter(
        Transfer.status == TransferStatus.AWAITING_PAYMENT,
    ).scalar()

    return {
        "funds_collected_today_zar": str(funds_collected_today),
        "funds_pending_processing_zar": str(funds_pending_processing),
        "funds_paid_out_zar": str(funds_paid_out),
        "outstanding_liabilities_zar": str(outstanding_liabilities),
        "revenue_today_zar": str(revenue_today),
        "revenue_month_zar": str(revenue_month),
        "awaiting_payment_zar": str(awaiting_payment),
        "completed_transfer_count": db.query(func.count(Transfer.id)).filter(
            Transfer.status == TransferStatus.COMPLETED
        ).scalar() or 0,
    }
