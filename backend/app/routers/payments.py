from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.customer_profile import CustomerProfile
from app.models.enums import UserRole
from app.models.payment_method import PaymentMethod
from app.models.payment_reference import PaymentReference
from app.models.transfer import Transfer
from app.models.user import User
from app.schemas.payment import (
    FlutterwaveSessionResponse,
    GeneratePaymentRequest,
    PaymentMethodResponse,
    PaymentReferenceResponse,
    PaymentStatusResponse,
)
from app.services.payment_collection import generate_payment_reference
from app.utils.voucher_pdf import generate_voucher_pdf

router = APIRouter(prefix="/payments", tags=["Payments"])
settings = get_settings()


@router.get("/methods", response_model=list[PaymentMethodResponse])
def list_payment_methods(db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(PaymentMethod)
        .filter(PaymentMethod.is_active.is_(True))
        .order_by(PaymentMethod.id.asc())
        .all()
    )


@router.post("/transfers/{transfer_id}/generate", response_model=PaymentReferenceResponse)
def generate_payment(
    transfer_id: int,
    data: GeneratePaymentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    transfer = (
        db.query(Transfer)
        .filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    method = (
        db.query(PaymentMethod)
        .filter(PaymentMethod.code == data.payment_method_code, PaymentMethod.is_active.is_(True))
        .first()
    )
    if not method:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment method")

    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    customer_name = f"{profile.first_name} {profile.last_name}" if profile else current_user.email

    try:
        payment_ref = generate_payment_reference(db, transfer, method, current_user, customer_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db.commit()
    db.refresh(payment_ref)
    return payment_ref


@router.get("/transfers/{transfer_id}/reference", response_model=PaymentReferenceResponse | None)
def get_payment_reference(
    transfer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    transfer = (
        db.query(Transfer)
        .filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    ref = (
        db.query(PaymentReference)
        .filter(PaymentReference.transfer_id == transfer_id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    return ref


@router.get("/transfers/{transfer_id}/voucher.pdf")
def download_voucher_pdf(
    transfer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    transfer = (
        db.query(Transfer)
        .filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    ref = (
        db.query(PaymentReference)
        .options(joinedload(PaymentReference.payment_method))
        .filter(PaymentReference.transfer_id == transfer_id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    if not ref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payment reference found")

    pdf_bytes = generate_voucher_pdf(
        transfer_reference=transfer.reference,
        payment_reference=ref.reference_number,
        voucher_number=ref.voucher_number,
        amount=str(ref.amount),
        expiry_date=str(ref.expiry_date) if ref.expiry_date else "N/A",
        barcode_data=ref.barcode_data,
        qr_data=ref.qr_data,
        payment_method=ref.payment_method.name if ref.payment_method else ref.provider,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="voucher-{transfer.reference}.pdf"'},
    )


@router.post("/transfers/{transfer_id}/mark-paid")
def mark_paid_stub(
    transfer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Dev/testing endpoint — simulates retailer payment confirmation for voucher methods."""
    if settings.is_production or not settings.enable_dev_endpoints:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not available in production")

    from app.models.enums import PaymentReferenceStatus, TransferStatus
    from app.services.payment_collection import log_payment_event, mark_reference_paid
    from app.models.enums import PaymentEventType
    from app.services.transfer import record_status_change

    transfer = db.query(Transfer).filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    ref = (
        db.query(PaymentReference)
        .options(joinedload(PaymentReference.payment_method))
        .filter(PaymentReference.transfer_id == transfer_id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    if not ref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payment reference")

    requires_proof = ref.payment_method.requires_proof_upload if ref.payment_method else False
    mark_reference_paid(db, ref, transfer, requires_proof_upload=requires_proof)
    db.commit()
    return {"message": "Payment marked as received (test mode)"}


@router.post("/transfers/{transfer_id}/flutterwave/session", response_model=FlutterwaveSessionResponse)
def create_flutterwave_session(
    transfer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create Flutterwave Checkout session — card, bank, Capitec Pay, 1Voucher, etc."""
    from datetime import UTC, datetime, timedelta

    transfer = (
        db.query(Transfer)
        .filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    method = (
        db.query(PaymentMethod)
        .filter(PaymentMethod.code.in_(("flutterwave", "card", "payfast")), PaymentMethod.is_active.is_(True))
        .order_by(PaymentMethod.id.asc())
        .first()
    )
    if not method:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Flutterwave payment method not configured")

    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    customer_name = f"{profile.first_name} {profile.last_name}" if profile else (current_user.first_name or "Customer")

    from app.models.enums import PaymentReferenceStatus

    existing = (
        db.query(PaymentReference)
        .filter(
            PaymentReference.transfer_id == transfer_id,
            PaymentReference.provider.in_(("flutterwave", "card")),
            PaymentReference.status == PaymentReferenceStatus.AWAITING_PAYMENT,
        )
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    if existing and existing.provider_metadata and existing.provider_metadata.get("payment_url"):
        return FlutterwaveSessionResponse(
            payment_url=existing.provider_metadata["payment_url"],
            session_ref=existing.reference_number,
            provider="flutterwave",
            status="pending",
            expires_at=(existing.expiry_date.isoformat() if existing.expiry_date else None),
        )

    try:
        payment_ref = generate_payment_reference(db, transfer, method, current_user, customer_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    payment_url = (payment_ref.provider_metadata or {}).get("payment_url")
    if not payment_url:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Flutterwave did not return a checkout URL")

    db.commit()
    db.refresh(payment_ref)

    return FlutterwaveSessionResponse(
        payment_url=payment_url,
        session_ref=payment_ref.reference_number,
        provider="flutterwave",
        status="pending",
        expires_at=(datetime.now(UTC) + timedelta(hours=24)).isoformat(),
    )


@router.get("/transfers/{transfer_id}/payment-status", response_model=PaymentStatusResponse)
def get_payment_status(
    transfer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    transfer = (
        db.query(Transfer)
        .filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    ref = (
        db.query(PaymentReference)
        .filter(PaymentReference.transfer_id == transfer_id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    payment_status = ref.status.value if ref and hasattr(ref.status, "value") else (str(ref.status) if ref else "none")
    transfer_status = transfer.status.value if hasattr(transfer.status, "value") else str(transfer.status)
    return PaymentStatusResponse(
        transfer_id=transfer_id,
        status=transfer_status,
        payment_status=payment_status,
        reference_number=ref.reference_number if ref else None,
    )
