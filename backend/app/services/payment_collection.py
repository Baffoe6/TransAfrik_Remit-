from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.models.enums import PaymentEventType, PaymentReferenceStatus, TransferStatus
from app.models.payment_event import PaymentEvent
from app.models.payment_method import PaymentMethod
from app.models.payment_reference import PaymentReference
from app.models.transfer import Transfer
from app.models.user import User
from app.payment_providers.base import PaymentReferenceRequest
from app.payment_providers.registry import get_payment_provider
from app.services.transfer import record_status_change


def log_payment_event(
    db: Session,
    transfer_id: int,
    event_type: PaymentEventType,
    *,
    provider_reference: str | None = None,
    raw_payload: dict | None = None,
    notes: str | None = None,
) -> PaymentEvent:
    event = PaymentEvent(
        transfer_id=transfer_id,
        event_type=event_type,
        event_timestamp=datetime.now(UTC),
        provider_reference=provider_reference,
        raw_payload=raw_payload,
        notes=notes,
    )
    db.add(event)
    db.flush()
    return event


def generate_payment_reference(
    db: Session,
    transfer: Transfer,
    payment_method: PaymentMethod,
    user: User,
    customer_name: str,
) -> PaymentReference:
    provider = get_payment_provider(payment_method.provider_class)
    request = PaymentReferenceRequest(
        transfer_reference=transfer.reference,
        amount=transfer.total_amount_zar,
        currency="ZAR",
        customer_name=customer_name,
        customer_email=user.email,
        customer_phone=user.phone,
    )
    result = provider.generate_reference(request)
    if not result.success:
        raise ValueError(result.message or "Failed to generate payment reference")

    payment_ref = PaymentReference(
        transfer_id=transfer.id,
        payment_method_id=payment_method.id,
        provider=payment_method.provider,
        reference_number=result.reference_number,
        voucher_number=result.voucher_number,
        barcode_data=result.barcode_data,
        qr_data=result.qr_data,
        amount=transfer.total_amount_zar,
        currency="ZAR",
        expiry_date=result.expiry_date,
        status=PaymentReferenceStatus.AWAITING_PAYMENT,
        banking_instructions=result.banking_instructions,
        provider_metadata=result.metadata,
    )
    db.add(payment_ref)
    transfer.payment_method_id = payment_method.id

    if transfer.status == TransferStatus.DRAFT:
        record_status_change(db, transfer, TransferStatus.AWAITING_PAYMENT, notes="Payment reference generated")

    log_payment_event(
        db,
        transfer.id,
        PaymentEventType.REFERENCE_GENERATED,
        provider_reference=result.reference_number,
        raw_payload={"provider": payment_method.provider},
    )
    db.flush()
    return payment_ref


def mark_reference_paid(
    db: Session,
    payment_ref: PaymentReference,
    transfer: Transfer,
    *,
    requires_proof_upload: bool = False,
) -> None:
    payment_ref.status = PaymentReferenceStatus.PAID
    log_payment_event(
        db, transfer.id, PaymentEventType.PAYMENT_RECEIVED, provider_reference=payment_ref.reference_number
    )

    if requires_proof_upload:
        record_status_change(db, transfer, TransferStatus.PAYMENT_PENDING_VERIFICATION, notes="Awaiting proof verification")
    else:
        record_status_change(db, transfer, TransferStatus.PAYMENT_VERIFIED, notes="Payment received")
        _route_after_payment_verified(db, transfer)


def _route_after_payment_verified(db: Session, transfer: Transfer) -> None:
    if transfer.aml_flags:
        record_status_change(db, transfer, TransferStatus.COMPLIANCE_REVIEW, notes="AML flags require review")
    else:
        transfer.compliance_approved = True
        record_status_change(db, transfer, TransferStatus.READY_FOR_PROCESSING, notes="Auto-approved — no AML flags")


def expire_stale_references(db: Session, today: date | None = None) -> int:
    today = today or datetime.now(UTC).date()
    expired = (
        db.query(PaymentReference)
        .filter(
            PaymentReference.expiry_date < today,
            PaymentReference.status == PaymentReferenceStatus.AWAITING_PAYMENT,
        )
        .all()
    )
    count = 0
    for ref in expired:
        ref.status = PaymentReferenceStatus.EXPIRED
        transfer = db.query(Transfer).filter(Transfer.id == ref.transfer_id).first()
        if transfer and transfer.status == TransferStatus.AWAITING_PAYMENT:
            record_status_change(db, transfer, TransferStatus.EXPIRED, notes="Payment reference expired")
        log_payment_event(db, ref.transfer_id, PaymentEventType.REFERENCE_EXPIRED, provider_reference=ref.reference_number)
        count += 1
    return count
