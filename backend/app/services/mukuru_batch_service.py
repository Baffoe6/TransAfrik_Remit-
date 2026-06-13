from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.enums import MukuruBatchStatus, MukuruSettlementStatus, OperationsAuditCategory, TransferStatus
from app.models.mukuru_operations import MukuruBatch, MukuruBatchItem, MukuruSettlement
from app.models.payment_reference import PaymentReference
from app.models.provider import Provider
from app.models.transfer import Transfer
from app.models.user import User
from app.providers.base import TransferRequest
from app.providers.registry import get_provider
from app.services.operations_audit import log_operations_action
from app.services.transfer import record_status_change
from app.utils.file_storage import ensure_upload_dir


def create_batch_from_transfers(
    db: Session,
    *,
    transfer_ids: list[int],
    created_by: int,
    export_format: str = "csv",
    ip_address: str | None = None,
) -> MukuruBatch:
    transfers = (
        db.query(Transfer)
        .filter(Transfer.id.in_(transfer_ids))
        .options(joinedload(Transfer.beneficiary), joinedload(Transfer.user).joinedload(User.profile))
        .all()
    )
    if not transfers:
        raise ValueError("No transfers found")

    provider_record = db.query(Provider).filter(Provider.code == "manual_mukuru", Provider.is_active.is_(True)).first()
    if not provider_record:
        raise ValueError("Manual Mukuru provider not configured")

    provider = get_provider(provider_record.provider_class)
    batch_dir = str(ensure_upload_dir() / "batches")

    transfer_requests: list[TransferRequest] = []
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

    if export_format == "xlsx" and hasattr(provider, "export_excel"):
        result = provider.export_excel(transfer_requests, batch_dir)
    else:
        result = provider.export_batch(transfer_requests, batch_dir)

    total_zar = sum((t.send_amount_zar for t in transfers), Decimal("0"))
    total_ghs = sum((t.receive_amount_ghs for t in transfers), Decimal("0"))

    batch = MukuruBatch(
        batch_id=result.batch_id,
        status=MukuruBatchStatus.PENDING_APPROVAL,
        file_path=result.file_path,
        file_format=result.file_format or export_format,
        transfer_count=result.transfer_count,
        total_amount_zar=total_zar,
        total_amount_ghs=total_ghs,
        created_by=created_by,
        export_metadata={"message": result.message},
    )
    db.add(batch)
    db.flush()

    for t in transfers:
        db.add(MukuruBatchItem(
            batch_id=batch.id,
            transfer_id=t.id,
            amount_zar=t.send_amount_zar,
            amount_ghs=t.receive_amount_ghs,
            status="pending",
        ))
        t.batch_export_id = result.batch_id
        t.provider_id = provider_record.id

    log_operations_action(
        db,
        category=OperationsAuditCategory.BATCH,
        action="batch_created",
        entity_type="mukuru_batch",
        user_id=created_by,
        entity_id=batch.id,
        details={"batch_id": result.batch_id, "transfer_ids": transfer_ids, "count": result.transfer_count},
        ip_address=ip_address,
    )
    db.flush()
    return batch


def approve_batch(db: Session, batch: MukuruBatch, *, approved_by: int, ip_address: str | None = None) -> MukuruBatch:
    if batch.status != MukuruBatchStatus.PENDING_APPROVAL:
        raise ValueError(f"Batch cannot be approved from status {batch.status.value}")
    batch.status = MukuruBatchStatus.APPROVED
    batch.approved_by = approved_by
    batch.approved_at = datetime.now(UTC)
    log_operations_action(
        db,
        category=OperationsAuditCategory.BATCH,
        action="batch_approved",
        entity_type="mukuru_batch",
        user_id=approved_by,
        entity_id=batch.id,
        details={"batch_id": batch.batch_id},
        ip_address=ip_address,
    )
    db.flush()
    return batch


def submit_batch(db: Session, batch: MukuruBatch, *, submitted_by: int, ip_address: str | None = None) -> MukuruBatch:
    if batch.status != MukuruBatchStatus.APPROVED:
        raise ValueError(f"Batch cannot be submitted from status {batch.status.value}")

    provider_record = db.query(Provider).filter(Provider.code == "manual_mukuru").first()
    provider = get_provider(provider_record.provider_class) if provider_record else None

    items = db.query(MukuruBatchItem).filter(MukuruBatchItem.batch_id == batch.id).all()
    for item in items:
        transfer = db.query(Transfer).filter(Transfer.id == item.transfer_id).first()
        if not transfer:
            continue
        if provider:
            result = provider.mark_as_submitted(transfer.reference)
            item.provider_reference = result.provider_reference
        item.status = "submitted"
        if transfer.status == TransferStatus.READY_FOR_PROCESSING:
            record_status_change(
                db, transfer, TransferStatus.SUBMITTED_TO_MUKURU,
                changed_by=submitted_by, notes=f"Batch {batch.batch_id} submitted",
            )

    batch.status = MukuruBatchStatus.SUBMITTED
    batch.submitted_at = datetime.now(UTC)
    log_operations_action(
        db,
        category=OperationsAuditCategory.BATCH,
        action="batch_submitted",
        entity_type="mukuru_batch",
        user_id=submitted_by,
        entity_id=batch.id,
        details={"batch_id": batch.batch_id},
        ip_address=ip_address,
    )
    db.flush()
    return batch


def reject_batch(db: Session, batch: MukuruBatch, *, rejected_by: int, reason: str, ip_address: str | None = None) -> MukuruBatch:
    batch.status = MukuruBatchStatus.REJECTED
    batch.notes = reason
    log_operations_action(
        db,
        category=OperationsAuditCategory.BATCH,
        action="batch_rejected",
        entity_type="mukuru_batch",
        user_id=rejected_by,
        entity_id=batch.id,
        details={"batch_id": batch.batch_id, "reason": reason},
        ip_address=ip_address,
    )
    db.flush()
    return batch


def record_mukuru_settlement(
    db: Session,
    *,
    settlement_reference: str,
    settlement_date,
    amount_zar: Decimal,
    amount_ghs: Decimal,
    batch_id: int | None,
    transfer_count: int,
    recorded_by: int,
    notes: str | None = None,
    raw_data: dict | None = None,
    ip_address: str | None = None,
) -> MukuruSettlement:
    expected_zar = Decimal("0")
    if batch_id:
        batch = db.query(MukuruBatch).filter(MukuruBatch.id == batch_id).first()
        if batch:
            expected_zar = batch.total_amount_zar

    variance = amount_zar - expected_zar if expected_zar else Decimal("0")
    status = MukuruSettlementStatus.MATCHED if variance == 0 else MukuruSettlementStatus.VARIANCE

    settlement = MukuruSettlement(
        batch_id=batch_id,
        settlement_reference=settlement_reference,
        settlement_date=settlement_date,
        amount_zar=amount_zar,
        amount_ghs=amount_ghs,
        transfer_count=transfer_count,
        status=status,
        variance_zar=variance,
        notes=notes,
        raw_data=raw_data,
        recorded_by=recorded_by,
    )
    db.add(settlement)

    if batch_id:
        batch = db.query(MukuruBatch).filter(MukuruBatch.id == batch_id).first()
        if batch and status == MukuruSettlementStatus.MATCHED:
            batch.status = MukuruBatchStatus.RECONCILED
            batch.reconciled_at = datetime.now(UTC)

    log_operations_action(
        db,
        category=OperationsAuditCategory.SETTLEMENT,
        action="mukuru_settlement_recorded",
        entity_type="mukuru_settlement",
        user_id=recorded_by,
        details={"reference": settlement_reference, "variance_zar": str(variance)},
        ip_address=ip_address,
    )
    db.flush()
    return settlement


def get_batch_reconciliation_summary(db: Session) -> dict:
    batches = db.query(MukuruBatch).order_by(MukuruBatch.created_at.desc()).limit(50).all()
    settlements = db.query(MukuruSettlement).order_by(MukuruSettlement.created_at.desc()).limit(20).all()

    by_status: dict[str, int] = {}
    for b in batches:
        key = b.status.value if hasattr(b.status, "value") else str(b.status)
        by_status[key] = by_status.get(key, 0) + 1

    total_variance = sum((s.variance_zar for s in settlements), Decimal("0"))

    return {
        "batches_by_status": by_status,
        "total_batches": len(batches),
        "pending_approval": sum(1 for b in batches if b.status == MukuruBatchStatus.PENDING_APPROVAL),
        "submitted": sum(1 for b in batches if b.status == MukuruBatchStatus.SUBMITTED),
        "reconciled": sum(1 for b in batches if b.status == MukuruBatchStatus.RECONCILED),
        "settlement_variance_zar": str(total_variance),
        "recent_settlements": [
            {
                "id": s.id,
                "reference": s.settlement_reference,
                "amount_zar": str(s.amount_zar),
                "status": s.status.value,
                "variance_zar": str(s.variance_zar),
                "settlement_date": str(s.settlement_date),
            }
            for s in settlements
        ],
    }
