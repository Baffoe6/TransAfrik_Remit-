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
from app.schemas.payment import GeneratePaymentRequest, PaymentMethodResponse, PaymentReferenceResponse
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
