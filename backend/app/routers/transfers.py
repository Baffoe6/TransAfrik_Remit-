import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.enums import BeneficiaryStatus, KycStatus, PaymentProofStatus, TransferStatus
from app.models.payment_method import PaymentMethod
from app.models.payment_proof import PaymentProof
from app.models.payment_reference import PaymentReference
from app.models.compliance import EnhancedDueDiligenceCase
from app.models.transfer import Transfer
from app.models.transfer_status_history import TransferStatusHistory
from app.models.user import User
from app.schemas.transfer import (
    CalculatorRequest,
    CalculatorResponse,
    PaymentReferenceBrief,
    TransferCreate,
    TransferDetailResponse,
    TransferResponse,
    TransferStatusHistoryResponse,
)
from app.services.compliance_engine import run_transfer_compliance
from app.services.payment_collection import generate_payment_reference, log_payment_event
from app.services.pricing import calculate_transfer_amounts
from app.services.timeline_service import build_realtime_tracking
from app.services.transfer import build_transfer_timeline, determine_initial_status, record_status_change

TRANSFER_AMOUNT_FIELDS = frozenset({"send_amount_zar", "fee_zar", "exchange_rate", "receive_amount_ghs", "total_amount_zar"})
from app.models.enums import PaymentEventType
from app.utils.file_storage import save_upload
from app.utils.reference import generate_transfer_reference

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("/calculate", response_model=CalculatorResponse)
def calculate(data: CalculatorRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        amounts = calculate_transfer_amounts(
            db,
            data.send_amount_zar,
            destination_country=data.destination_country,
            payment_method_id=data.payment_method_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return CalculatorResponse(**amounts)


@router.get("", response_model=list[TransferResponse])
def list_transfers(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(Transfer)
        .filter(Transfer.user_id == current_user.id)
        .order_by(Transfer.created_at.desc())
        .all()
    )


@router.post("", response_model=TransferDetailResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    data: TransferCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile required")

    beneficiary = (
        db.query(Beneficiary)
        .filter(
            Beneficiary.id == data.beneficiary_id,
            Beneficiary.user_id == current_user.id,
            Beneficiary.is_active.is_(True),
        )
        .first()
    )
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    if beneficiary.status == BeneficiaryStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Beneficiary has been rejected")

    from app.services.pilot_service import check_transfer_limits

    check_transfer_limits(db, current_user.id, data.send_amount_zar, beneficiary)

    payment_method_id = None
    if data.payment_method_code:
        method_lookup = (
            db.query(PaymentMethod)
            .filter(PaymentMethod.code == data.payment_method_code, PaymentMethod.is_active.is_(True))
            .first()
        )
        if method_lookup:
            payment_method_id = method_lookup.id

    try:
        amounts = calculate_transfer_amounts(
            db,
            data.send_amount_zar,
            destination_country=beneficiary.country,
            payment_method_id=payment_method_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    compliance = run_transfer_compliance(
        db,
        user_id=current_user.id,
        send_amount_zar=data.send_amount_zar,
        beneficiary=beneficiary,
        profile=profile,
    )

    initial_status = determine_initial_status(profile.kyc_status)
    transfer = Transfer(
        reference=generate_transfer_reference(),
        user_id=current_user.id,
        beneficiary_id=beneficiary.id,
        status=initial_status,
        aml_flags=compliance["aml_flags"] if compliance["aml_flags"] else None,
        risk_score=compliance["risk_score"],
        **{k: v for k, v in amounts.items() if k in TRANSFER_AMOUNT_FIELDS},
    )
    db.add(transfer)
    db.flush()

    if compliance.get("edd_case_id"):
        edd = db.query(EnhancedDueDiligenceCase).filter(EnhancedDueDiligenceCase.id == compliance["edd_case_id"]).first()
        if edd:
            edd.transfer_id = transfer.id

    record_status_change(db, transfer, initial_status, changed_by=current_user.id, notes="Transfer created")

    payment_ref = None
    if data.payment_method_code and profile.kyc_status == KycStatus.APPROVED:
        method = (
            db.query(PaymentMethod)
            .filter(PaymentMethod.code == data.payment_method_code, PaymentMethod.is_active.is_(True))
            .first()
        )
        if method:
            customer_name = f"{profile.first_name} {profile.last_name}"
            payment_ref = generate_payment_reference(db, transfer, method, current_user, customer_name)

    db.commit()
    db.refresh(transfer)
    return _to_detail(transfer, payment_ref, db)


@router.get("/{transfer_id}", response_model=TransferDetailResponse)
def get_transfer(
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

    payment_ref = (
        db.query(PaymentReference)
        .filter(PaymentReference.transfer_id == transfer_id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    return _to_detail(transfer, payment_ref, db)


@router.get("/{transfer_id}/timeline")
def get_transfer_timeline(
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

    history = (
        db.query(TransferStatusHistory)
        .filter(TransferStatusHistory.transfer_id == transfer_id)
        .order_by(TransferStatusHistory.created_at.asc())
        .all()
    )
    return {"reference": transfer.reference, "status": transfer.status.value, "timeline": build_transfer_timeline(transfer, history)}


@router.get("/{transfer_id}/tracking")
def get_transfer_tracking(
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
    return build_realtime_tracking(db, transfer)


@router.get("/{transfer_id}/tracking/stream")
async def stream_transfer_tracking(
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

    async def event_generator():
        for _ in range(60):
            db.refresh(transfer)
            payload = build_realtime_tracking(db, transfer)
            yield f"data: {json.dumps(payload)}\n\n"
            if payload.get("is_terminal"):
                break
            await asyncio.sleep(3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{transfer_id}/history", response_model=list[TransferStatusHistoryResponse])
def get_transfer_history(
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

    return (
        db.query(TransferStatusHistory)
        .filter(TransferStatusHistory.transfer_id == transfer_id)
        .order_by(TransferStatusHistory.created_at.asc())
        .all()
    )


@router.post("/{transfer_id}/payment-proof", status_code=status.HTTP_201_CREATED)
async def upload_payment_proof(
    transfer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    transfer = (
        db.query(Transfer)
        .filter(Transfer.id == transfer_id, Transfer.user_id == current_user.id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    allowed = (
        TransferStatus.AWAITING_PAYMENT,
        TransferStatus.PAYMENT_PENDING_VERIFICATION,
    )
    if transfer.status not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot upload payment proof for this transfer")

    file_path, original_filename = await save_upload(file, f"payments/{transfer.id}")

    proof = PaymentProof(
        transfer_id=transfer.id,
        file_path=file_path,
        original_filename=original_filename,
        status=PaymentProofStatus.PENDING,
    )
    db.add(proof)
    log_payment_event(db, transfer.id, PaymentEventType.PROOF_UPLOADED, notes=original_filename)

    if transfer.status == TransferStatus.AWAITING_PAYMENT:
        record_status_change(db, transfer, TransferStatus.PAYMENT_PENDING_VERIFICATION, changed_by=current_user.id, notes="Payment proof uploaded")

    db.commit()
    return {"message": "Payment proof uploaded", "id": proof.id}


def _to_detail(transfer: Transfer, payment_ref: PaymentReference | None, db: Session) -> TransferDetailResponse:
    history = (
        db.query(TransferStatusHistory)
        .filter(TransferStatusHistory.transfer_id == transfer.id)
        .order_by(TransferStatusHistory.created_at.asc())
        .all()
    )
    ref_brief = None
    if payment_ref:
        ref_brief = PaymentReferenceBrief(
            reference_number=payment_ref.reference_number,
            voucher_number=payment_ref.voucher_number,
            barcode_data=payment_ref.barcode_data,
            qr_data=payment_ref.qr_data,
            expiry_date=str(payment_ref.expiry_date) if payment_ref.expiry_date else None,
            status=payment_ref.status.value if hasattr(payment_ref.status, "value") else payment_ref.status,
            banking_instructions=payment_ref.banking_instructions,
        )
    base = TransferResponse.model_validate(transfer)
    return TransferDetailResponse(
        **base.model_dump(),
        payment_reference=ref_brief,
        timeline=build_transfer_timeline(transfer, history),
    )
