from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_client_ip, require_roles
from app.models.audit_log import AuditLog
from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.enums import (
    BeneficiaryStatus,
    KycStatus,
    PaymentProofStatus,
    TransferStatus,
    UserRole,
)
from app.models.exchange_rate import ExchangeRate
from app.models.fee_rule import FeeRule
from app.models.kyc_document import KycDocument
from app.models.payment_proof import PaymentProof
from app.models.payment_reference import PaymentReference
from app.models.payment_verification import PaymentVerification
from app.models.provider import Provider
from app.models.transfer import Transfer
from app.models.user import User
from app.models.enums import PaymentEventType, PaymentReferenceStatus
from app.models.payment_event import PaymentEvent
from app.providers.base import TransferRequest
from app.providers.registry import get_provider
from app.schemas.admin import (
    AuditLogResponse,
    BatchExportRequest,
    BeneficiaryReviewRequest,
    CustomerListItem,
    DashboardStats,
    ExchangeRateCreate,
    FeeRuleCreate,
    KycReviewRequest,
    PaymentVerifyRequest,
)
from app.schemas.beneficiary import BeneficiaryResponse
from app.schemas.kyc import KycDocumentResponse
from app.schemas.payment import ComplianceQueueItem, PaymentDashboardStats, PaymentVerificationRequest
from app.schemas.transfer import TransferResponse, TransferStatusUpdate
from app.services.audit import log_action
from app.services.payment_collection import _route_after_payment_verified, expire_stale_references, log_payment_event
from app.services.transfer import record_status_change
from app.utils.file_serve import serve_upload_file
from app.utils.file_storage import ensure_upload_dir

router = APIRouter(prefix="/admin", tags=["Admin"])
settings = get_settings()

AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    total_customers = db.query(func.count(User.id)).filter(User.role == UserRole.CUSTOMER).scalar() or 0
    pending_kyc = (
        db.query(func.count(CustomerProfile.id))
        .filter(CustomerProfile.kyc_status == KycStatus.PENDING)
        .scalar()
        or 0
    )
    pending_transfers = (
        db.query(func.count(Transfer.id))
        .filter(
            Transfer.status.in_([
                TransferStatus.DRAFT,
                TransferStatus.AWAITING_PAYMENT,
                TransferStatus.PAYMENT_PENDING_VERIFICATION,
                TransferStatus.COMPLIANCE_REVIEW,
                TransferStatus.READY_FOR_PROCESSING,
            ])
        )
        .scalar()
        or 0
    )
    completed_transfers = (
        db.query(func.count(Transfer.id)).filter(Transfer.status == TransferStatus.COMPLETED).scalar() or 0
    )

    month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_volume = (
        db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0))
        .filter(Transfer.created_at >= month_start, Transfer.status == TransferStatus.COMPLETED)
        .scalar()
    )

    return DashboardStats(
        total_customers=total_customers,
        pending_kyc=pending_kyc,
        pending_transfers=pending_transfers,
        completed_transfers=completed_transfers,
        monthly_volume_zar=Decimal(str(monthly_volume)),
    )


@router.get("/customers", response_model=list[CustomerListItem])
def list_customers(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    search: str | None = None,
):
    from sqlalchemy import or_

    q = (
        db.query(User)
        .filter(User.role == UserRole.CUSTOMER)
        .options(joinedload(User.profile))
        .outerjoin(CustomerProfile, CustomerProfile.user_id == User.id)
    )
    if search:
        term = f"%{search.strip()}%"
        filters = [
            User.mobile_number.ilike(term),
            User.email.ilike(term),
            User.first_name.ilike(term),
            User.last_name.ilike(term),
            CustomerProfile.first_name.ilike(term),
            CustomerProfile.last_name.ilike(term),
        ]
        if search.strip().isdigit():
            filters.append(User.id == int(search.strip()))
        q = q.filter(or_(*filters))
    customers = q.order_by(User.created_at.desc()).all()
    result = []
    for c in customers:
        transfer_count = db.query(func.count(Transfer.id)).filter(Transfer.user_id == c.id).scalar() or 0
        result.append(CustomerListItem(
            id=c.id,
            email=c.email,
            mobile_number=c.mobile_number,
            first_name=c.first_name or (c.profile.first_name if c.profile else None),
            last_name=c.last_name or (c.profile.last_name if c.profile else None),
            kyc_status=c.profile.kyc_status.value if c.profile else None,
            status=c.status,
            created_at=c.created_at,
            transfer_count=transfer_count,
        ))
    return result


@router.get("/kyc/pending")
def pending_kyc(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    profiles = (
        db.query(CustomerProfile)
        .filter(CustomerProfile.kyc_status == KycStatus.PENDING)
        .options(joinedload(CustomerProfile.user))
        .all()
    )
    return [
        {
            "user_id": p.user_id,
            "email": p.user.email,
            "mobile_number": p.user.mobile_number,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "kyc_status": p.kyc_status.value,
            "documents": [
                KycDocumentResponse.model_validate(d)
                for d in db.query(KycDocument).filter(KycDocument.user_id == p.user_id).all()
            ],
        }
        for p in profiles
    ]


@router.post("/kyc/{user_id}/review")
def review_kyc(
    user_id: int,
    data: KycReviewRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    try:
        new_status = KycStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    if new_status not in (KycStatus.APPROVED, KycStatus.REJECTED):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status must be approved or rejected")

    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    profile.kyc_status = new_status
    profile.kyc_reviewed_at = datetime.now(UTC)
    profile.kyc_reviewed_by = admin.id
    profile.kyc_rejection_reason = data.rejection_reason if new_status == KycStatus.REJECTED else None
    if data.review_notes:
        profile.kyc_review_notes = data.review_notes

    user = db.query(User).filter(User.id == user_id).first()
    if new_status == KycStatus.APPROVED and user:
        user.phone_verified = True

    db.query(KycDocument).filter(KycDocument.user_id == user_id).update({
        KycDocument.status: new_status,
        KycDocument.reviewed_by: admin.id,
        KycDocument.reviewed_at: datetime.now(UTC),
    })

    if new_status == KycStatus.APPROVED:
        pending = (
            db.query(Transfer)
            .filter(Transfer.user_id == user_id, Transfer.status == TransferStatus.DRAFT)
            .all()
        )
        for t in pending:
            record_status_change(
                db, t, TransferStatus.DRAFT, changed_by=admin.id,
                notes="KYC approved — select payment method to continue",
            )

    log_action(
        db,
        user_id=admin.id,
        action="kyc_review",
        entity_type="customer_profile",
        entity_id=profile.id,
        details={"user_id": user_id, "status": new_status.value},
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": f"KYC {new_status.value}"}


@router.get("/beneficiaries/pending", response_model=list[BeneficiaryResponse])
def pending_beneficiaries(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(Beneficiary)
        .filter(Beneficiary.status == BeneficiaryStatus.PENDING)
        .order_by(Beneficiary.created_at.asc())
        .all()
    )


@router.post("/beneficiaries/{beneficiary_id}/review")
def review_beneficiary(
    beneficiary_id: int,
    data: BeneficiaryReviewRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    try:
        new_status = BeneficiaryStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    beneficiary.status = new_status
    beneficiary.reviewed_by = admin.id
    beneficiary.reviewed_at = datetime.now(UTC)
    beneficiary.rejection_reason = data.rejection_reason if new_status == BeneficiaryStatus.REJECTED else None

    log_action(
        db,
        user_id=admin.id,
        action="beneficiary_review",
        entity_type="beneficiary",
        entity_id=beneficiary.id,
        details={"status": new_status.value},
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": f"Beneficiary {new_status.value}"}


@router.get("/transfers", response_model=list[TransferResponse])
def list_all_transfers(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    status_filter: str | None = None,
):
    query = db.query(Transfer).order_by(Transfer.created_at.desc())
    if status_filter:
        try:
            query = query.filter(Transfer.status == TransferStatus(status_filter))
        except ValueError:
            pass
    return query.limit(200).all()


@router.get("/transfers/{transfer_id}", response_model=TransferResponse)
def get_transfer_admin(transfer_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    return transfer


@router.patch("/transfers/{transfer_id}/status")
def update_transfer_status(
    transfer_id: int,
    data: TransferStatusUpdate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    try:
        new_status = TransferStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    record_status_change(db, transfer, new_status, changed_by=admin.id, notes=data.notes)
    if data.rejection_reason:
        transfer.rejection_reason = data.rejection_reason
    if new_status == TransferStatus.COMPLETED:
        transfer.completed_at = datetime.now(UTC)

    log_action(
        db,
        user_id=admin.id,
        action="transfer_status_update",
        entity_type="transfer",
        entity_id=transfer.id,
        details={"status": new_status.value, "notes": data.notes},
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": f"Transfer status updated to {new_status.value}"}


@router.post("/transfers/{transfer_id}/payment/verify")
def verify_payment(
    transfer_id: int,
    data: PaymentVerifyRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    try:
        proof_status = PaymentProofStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    proof = (
        db.query(PaymentProof)
        .filter(PaymentProof.transfer_id == transfer_id)
        .order_by(PaymentProof.created_at.desc())
        .first()
    )
    if not proof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payment proof found")

    proof.status = proof_status
    proof.verified_by = admin.id
    proof.verified_at = datetime.now(UTC)
    proof.rejection_reason = data.rejection_reason if proof_status == PaymentProofStatus.REJECTED else None

    verification = PaymentVerification(
        transfer_id=transfer_id,
        verified_by=admin.id if proof_status == PaymentProofStatus.VERIFIED else None,
        verified_at=datetime.now(UTC) if proof_status == PaymentProofStatus.VERIFIED else None,
        status=proof_status.value,
        notes=data.rejection_reason if hasattr(data, "rejection_reason") else None,
        rejection_reason=data.rejection_reason if proof_status == PaymentProofStatus.REJECTED else None,
    )
    db.add(verification)

    if proof_status == PaymentProofStatus.VERIFIED:
        record_status_change(db, transfer, TransferStatus.PAYMENT_VERIFIED, changed_by=admin.id, notes="Payment verified")
        _route_after_payment_verified(db, transfer)
        log_payment_event(db, transfer_id, PaymentEventType.PAYMENT_VERIFIED, notes="Admin verified payment")
    elif proof_status == PaymentProofStatus.REJECTED:
        record_status_change(db, transfer, TransferStatus.AWAITING_PAYMENT, changed_by=admin.id, notes="Payment rejected")

    log_action(
        db,
        user_id=admin.id,
        action="payment_verify",
        entity_type="payment_proof",
        entity_id=proof.id,
        details={"status": proof_status.value, "transfer_id": transfer_id},
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": f"Payment {proof_status.value}"}


@router.post("/transfers/export-batch")
def export_batch(
    data: BatchExportRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    transfers = (
        db.query(Transfer)
        .filter(Transfer.id.in_(data.transfer_ids))
        .options(joinedload(Transfer.beneficiary), joinedload(Transfer.user).joinedload(User.profile))
        .all()
    )
    if not transfers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transfers found")

    provider_record = db.query(Provider).filter(Provider.code == "manual_mukuru", Provider.is_active.is_(True)).first()
    if not provider_record:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Manual Mukuru provider not configured")

    provider = get_provider(provider_record.provider_class)
    batch_dir = str(ensure_upload_dir() / "batches")

    transfer_requests = []
    for t in transfers:
        profile = t.user.profile
        pay_ref = (
            db.query(PaymentReference)
            .filter(PaymentReference.transfer_id == t.id)
            .order_by(PaymentReference.created_at.desc())
            .first()
        )
        transfer_requests.append(TransferRequest(
            transfer_id=t.id,
            reference=t.reference,
            sender_name=f"{profile.first_name} {profile.last_name}" if profile else t.user.email,
            sender_phone=t.user.mobile_number,
            sender_id_number=profile.id_number if profile else None,
            beneficiary_name=t.beneficiary.full_name,
            beneficiary_country=t.beneficiary.country,
            mobile_money_provider=t.beneficiary.mobile_money_provider,
            mobile_wallet_number=t.beneficiary.mobile_wallet_number,
            send_amount_zar=t.send_amount_zar,
            receive_amount_ghs=t.receive_amount_ghs,
            exchange_rate=t.exchange_rate,
            fee_zar=t.fee_zar,
            payment_reference=pay_ref.reference_number if pay_ref else None,
            status=t.status.value,
        ))

    export_format = getattr(data, "format", "csv") if hasattr(data, "format") else "csv"
    if export_format == "xlsx" and hasattr(provider, "export_excel"):
        result = provider.export_excel(transfer_requests, batch_dir)
    else:
        result = provider.export_batch(transfer_requests, batch_dir)

    for t in transfers:
        t.batch_export_id = result.batch_id
        t.provider_id = provider_record.id
        provider.mark_as_submitted(t.reference)
        if t.status == TransferStatus.READY_FOR_PROCESSING:
            record_status_change(
                db, t, TransferStatus.SUBMITTED_TO_MUKURU, changed_by=admin.id, notes=f"Batch {result.batch_id}"
            )

    log_action(
        db,
        user_id=admin.id,
        action="batch_export",
        entity_type="batch",
        details={"batch_id": result.batch_id, "transfer_ids": data.transfer_ids, "count": result.transfer_count},
        ip_address=get_client_ip(request),
    )
    db.commit()

    return {
        "batch_id": result.batch_id,
        "file_path": result.file_path,
        "transfer_count": result.transfer_count,
        "message": result.message,
        "download_url": f"/admin/batches/{result.batch_id}/download",
    }


@router.get("/batches/{batch_id}/download")
def download_batch(batch_id: str, admin: AdminUser):
    batch_path = ensure_upload_dir() / "batches" / f"{batch_id}.csv"
    if not batch_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch file not found")
    return FileResponse(batch_path, filename=f"{batch_id}.csv", media_type="text/csv")


@router.get("/exchange-rates")
def list_exchange_rates(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rates = db.query(ExchangeRate).order_by(ExchangeRate.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "from_currency": r.from_currency,
            "to_currency": r.to_currency,
            "rate": str(r.rate),
            "is_active": r.is_active,
            "created_at": r.created_at,
        }
        for r in rates
    ]


@router.post("/exchange-rates", status_code=status.HTTP_201_CREATED)
def create_exchange_rate(
    data: ExchangeRateCreate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == data.from_currency,
        ExchangeRate.to_currency == data.to_currency,
    ).update({ExchangeRate.is_active: False})

    rate = ExchangeRate(
        from_currency=data.from_currency,
        to_currency=data.to_currency,
        rate=data.rate,
        is_active=True,
        created_by=admin.id,
    )
    db.add(rate)
    log_action(
        db,
        user_id=admin.id,
        action="exchange_rate_create",
        entity_type="exchange_rate",
        details={"rate": str(data.rate)},
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": "Exchange rate created", "id": rate.id}


@router.get("/fee-rules")
def list_fee_rules(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    rules = db.query(FeeRule).order_by(FeeRule.min_amount_zar.asc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "min_amount_zar": str(r.min_amount_zar),
            "max_amount_zar": str(r.max_amount_zar) if r.max_amount_zar else None,
            "fee_type": r.fee_type,
            "fee_value": str(r.fee_value),
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.post("/fee-rules", status_code=status.HTTP_201_CREATED)
def create_fee_rule(
    data: FeeRuleCreate,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    rule = FeeRule(**data.model_dump(), created_by=admin.id)
    db.add(rule)
    log_action(
        db,
        user_id=admin.id,
        action="fee_rule_create",
        entity_type="fee_rule",
        details=data.model_dump(mode="json"),
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": "Fee rule created", "id": rule.id}


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs(admin: AdminUser, db: Annotated[Session, Depends(get_db)], limit: int = 100):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()


@router.get("/kyc/documents/{document_id}/file")
def download_kyc_document(document_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    doc = db.query(KycDocument).filter(KycDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return serve_upload_file(doc.file_path, doc.original_filename)


@router.get("/transfers/{transfer_id}/payment-proof/file")
def download_payment_proof(transfer_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    proof = (
        db.query(PaymentProof)
        .filter(PaymentProof.transfer_id == transfer_id)
        .order_by(PaymentProof.created_at.desc())
        .first()
    )
    if not proof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payment proof found")
    return serve_upload_file(proof.file_path, proof.original_filename)


@router.get("/support/tickets")
def list_support_tickets(admin: AdminUser, db: Annotated[Session, Depends(get_db)], status_filter: str | None = None):
    from app.models.support_ticket import SupportTicket
    from app.models.enums import SupportTicketStatus

    query = db.query(SupportTicket).options(joinedload(SupportTicket.user)).order_by(SupportTicket.created_at.desc())
    if status_filter:
        try:
            query = query.filter(SupportTicket.status == SupportTicketStatus(status_filter))
        except ValueError:
            pass
    tickets = query.limit(100).all()
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "email": t.user.email if t.user else None,
            "subject": t.subject,
            "message": t.message,
            "status": t.status.value,
            "resolution": t.resolution,
            "created_at": t.created_at.isoformat(),
        }
        for t in tickets
    ]


@router.patch("/support/tickets/{ticket_id}")
def update_support_ticket(
    ticket_id: int,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    status: str = Query(...),
    resolution: str | None = Query(None),
):
    from app.models.support_ticket import SupportTicket
    from app.models.enums import SupportTicketStatus

    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    ticket.status = SupportTicketStatus(status)
    ticket.assigned_to = admin.id
    if resolution:
        ticket.resolution = resolution
    log_action(db, user_id=admin.id, action="support_ticket_update", entity_type="support_ticket",
               entity_id=ticket_id, details={"status": status}, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Ticket updated"}


@router.get("/payments/dashboard", response_model=PaymentDashboardStats)
def payment_dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    expire_stale_references(db)
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today_start.replace(day=1)

    pending_payments = db.query(func.count(Transfer.id)).filter(
        Transfer.status == TransferStatus.AWAITING_PAYMENT
    ).scalar() or 0
    pending_verifications = db.query(func.count(Transfer.id)).filter(
        Transfer.status == TransferStatus.PAYMENT_PENDING_VERIFICATION
    ).scalar() or 0
    expired_refs = db.query(func.count(PaymentReference.id)).filter(
        PaymentReference.status == PaymentReferenceStatus.EXPIRED
    ).scalar() or 0
    paid_today = db.query(func.count(PaymentEvent.id)).filter(
        PaymentEvent.event_type == PaymentEventType.PAYMENT_RECEIVED,
        PaymentEvent.event_timestamp >= today_start,
    ).scalar() or 0
    daily_volume = db.query(func.coalesce(func.sum(Transfer.total_amount_zar), 0)).filter(
        Transfer.created_at >= today_start,
        Transfer.status.notin_([TransferStatus.FAILED, TransferStatus.EXPIRED]),
    ).scalar()
    monthly_volume = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.created_at >= month_start,
        Transfer.status == TransferStatus.COMPLETED,
    ).scalar()

    db.commit()
    return PaymentDashboardStats(
        pending_payments=pending_payments,
        pending_verifications=pending_verifications,
        expired_references=expired_refs,
        paid_today=paid_today,
        daily_volume_zar=Decimal(str(daily_volume)),
        monthly_volume_zar=Decimal(str(monthly_volume)),
    )


@router.get("/payments/pending-verification")
def pending_payment_verifications(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    transfers = (
        db.query(Transfer)
        .filter(Transfer.status == TransferStatus.PAYMENT_PENDING_VERIFICATION)
        .options(
            joinedload(Transfer.user).joinedload(User.profile),
            joinedload(Transfer.beneficiary),
            joinedload(Transfer.payment_references),
            joinedload(Transfer.payment_proofs),
        )
        .order_by(Transfer.created_at.asc())
        .all()
    )
    return [_payment_detail(t) for t in transfers]


@router.get("/payments/transfers/{transfer_id}")
def payment_transfer_detail(transfer_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    transfer = (
        db.query(Transfer)
        .options(
            joinedload(Transfer.user).joinedload(User.profile),
            joinedload(Transfer.beneficiary),
            joinedload(Transfer.payment_references),
            joinedload(Transfer.payment_proofs),
        )
        .filter(Transfer.id == transfer_id)
        .first()
    )
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    return _payment_detail(transfer)


@router.post("/payments/transfers/{transfer_id}/verify")
def verify_payment_full(
    transfer_id: int,
    data: PaymentVerificationRequest,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    verification = PaymentVerification(
        transfer_id=transfer_id,
        verified_by=admin.id if data.status == "verified" else None,
        verified_at=datetime.now(UTC) if data.status == "verified" else None,
        status=data.status,
        notes=data.notes,
        rejection_reason=data.rejection_reason,
    )
    db.add(verification)

    if data.status == "verified":
        record_status_change(db, transfer, TransferStatus.PAYMENT_VERIFIED, changed_by=admin.id, notes=data.notes)
        _route_after_payment_verified(db, transfer)
        pay_ref = db.query(PaymentReference).filter(PaymentReference.transfer_id == transfer_id).first()
        if pay_ref:
            pay_ref.status = PaymentReferenceStatus.VERIFIED
    elif data.status == "rejected":
        record_status_change(db, transfer, TransferStatus.AWAITING_PAYMENT, changed_by=admin.id, notes=data.rejection_reason)
        transfer.rejection_reason = data.rejection_reason
    elif data.status == "more_info":
        record_status_change(db, transfer, TransferStatus.AWAITING_PAYMENT, changed_by=admin.id, notes="More information requested")

    log_action(db, user_id=admin.id, action="payment_verify", entity_type="transfer", entity_id=transfer_id,
               details={"status": data.status}, ip_address=get_client_ip(request))
    db.commit()
    return {"message": f"Payment {data.status}"}


@router.get("/compliance/queue", response_model=list[ComplianceQueueItem])
def compliance_queue(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    transfers = (
        db.query(Transfer)
        .filter(Transfer.status == TransferStatus.COMPLIANCE_REVIEW)
        .options(joinedload(Transfer.user).joinedload(User.profile))
        .order_by(Transfer.risk_score.desc())
        .all()
    )
    return [
        ComplianceQueueItem(
            transfer_id=t.id,
            reference=t.reference,
            customer_email=t.user.email,
            customer_name=f"{t.user.profile.first_name} {t.user.profile.last_name}" if t.user.profile else t.user.email,
            send_amount_zar=t.send_amount_zar,
            risk_score=t.risk_score,
            aml_flags=t.aml_flags,
            status=t.status.value,
            created_at=t.created_at,
        )
        for t in transfers
    ]


@router.post("/compliance/transfers/{transfer_id}/approve")
def compliance_approve(
    transfer_id: int,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    transfer.compliance_approved = True
    transfer.compliance_approved_by = admin.id
    transfer.compliance_approved_at = datetime.now(UTC)
    record_status_change(db, transfer, TransferStatus.READY_FOR_PROCESSING, changed_by=admin.id, notes="Compliance approved")
    log_action(db, user_id=admin.id, action="compliance_approve", entity_type="transfer", entity_id=transfer_id,
               ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Compliance approved"}


@router.post("/compliance/transfers/{transfer_id}/reject")
def compliance_reject(
    transfer_id: int,
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    reason: str = "Compliance rejection",
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    transfer.rejection_reason = reason
    record_status_change(db, transfer, TransferStatus.FAILED, changed_by=admin.id, notes=reason)
    log_action(db, user_id=admin.id, action="compliance_reject", entity_type="transfer", entity_id=transfer_id,
               ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Transfer rejected"}


def _payment_detail(transfer: Transfer) -> dict:
    profile = transfer.user.profile
    pay_ref = transfer.payment_references[0] if transfer.payment_references else None
    proof = transfer.payment_proofs[0] if transfer.payment_proofs else None
    return {
        "transfer": TransferResponse.model_validate(transfer),
        "customer": {
            "email": transfer.user.email,
            "mobile_number": transfer.user.mobile_number,
            "name": f"{profile.first_name} {profile.last_name}" if profile else None,
        },
        "beneficiary": {
            "full_name": transfer.beneficiary.full_name,
            "mobile_money_provider": transfer.beneficiary.mobile_money_provider,
            "mobile_wallet_number": transfer.beneficiary.mobile_wallet_number,
            "country": transfer.beneficiary.country,
        },
        "payment_reference": {
            "reference_number": pay_ref.reference_number,
            "voucher_number": pay_ref.voucher_number,
            "amount": str(pay_ref.amount),
            "status": pay_ref.status.value,
            "expiry_date": str(pay_ref.expiry_date) if pay_ref.expiry_date else None,
            "banking_instructions": pay_ref.banking_instructions,
        } if pay_ref else None,
        "payment_proof": {
            "filename": proof.original_filename,
            "status": proof.status.value,
        } if proof else None,
    }


@router.get("/reports/summary")
def reports_summary(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    by_status = (
        db.query(Transfer.status, func.count(Transfer.id))
        .group_by(Transfer.status)
        .all()
    )
    total_volume = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.status == TransferStatus.COMPLETED
    ).scalar()

    return {
        "transfers_by_status": {s.value: c for s, c in by_status},
        "total_completed_volume_zar": str(total_volume),
        "aml_flagged_transfers": db.query(func.count(Transfer.id)).filter(Transfer.aml_flags.isnot(None)).scalar() or 0,
    }
