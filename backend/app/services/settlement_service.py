from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import OperationsAuditCategory, PaymentReferenceStatus, PaymentSettlementStatus, TransferStatus
from app.models.mukuru_operations import MukuruSettlement
from app.models.payment_reference import PaymentReference
from app.models.settlement import PaymentSettlement
from app.models.transfer import Transfer
from app.services.operations_audit import log_operations_action


def _provider_collections(db: Session, provider: str) -> dict:
    refs = (
        db.query(PaymentReference)
        .filter(
            PaymentReference.provider == provider,
            PaymentReference.status.in_([PaymentReferenceStatus.PAID, PaymentReferenceStatus.VERIFIED]),
        )
        .all()
    )
    total = sum((r.amount for r in refs), Decimal("0"))
    return {"provider": provider, "transaction_count": len(refs), "collected_zar": str(total)}


def get_settlement_dashboard(db: Session) -> dict:
    pay_at = _provider_collections(db, "pay_at")
    easy_pay = _provider_collections(db, "easy_pay")
    eft = _provider_collections(db, "eft")

    mukuru_payouts = db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0)).filter(
        Transfer.status == TransferStatus.COMPLETED,
    ).scalar()

    mukuru_settlements = (
        db.query(MukuruSettlement)
        .order_by(MukuruSettlement.created_at.desc())
        .limit(10)
        .all()
    )

    payment_settlements = (
        db.query(PaymentSettlement)
        .order_by(PaymentSettlement.settlement_date.desc())
        .limit(20)
        .all()
    )

    total_variance = sum((s.variance_zar for s in payment_settlements), Decimal("0"))
    total_variance += sum((s.variance_zar for s in mukuru_settlements), Decimal("0"))

    return {
        "pay_at_collections": pay_at,
        "easy_pay_collections": easy_pay,
        "eft_collections": eft,
        "mukuru_payouts_zar": str(mukuru_payouts),
        "total_variance_zar": str(total_variance),
        "payment_settlements": [
            {
                "id": s.id,
                "provider": s.provider,
                "settlement_date": str(s.settlement_date),
                "expected_zar": str(s.expected_amount_zar),
                "collected_zar": str(s.collected_amount_zar),
                "variance_zar": str(s.variance_zar),
                "status": s.status.value,
                "transaction_count": s.transaction_count,
            }
            for s in payment_settlements
        ],
        "mukuru_settlements": [
            {
                "id": s.id,
                "reference": s.settlement_reference,
                "amount_zar": str(s.amount_zar),
                "variance_zar": str(s.variance_zar),
                "status": s.status.value,
            }
            for s in mukuru_settlements
        ],
    }


def record_payment_settlement(
    db: Session,
    *,
    provider: str,
    settlement_date: date,
    expected_amount_zar: Decimal,
    collected_amount_zar: Decimal,
    transaction_count: int,
    recorded_by: int,
    notes: str | None = None,
    raw_data: dict | None = None,
    ip_address: str | None = None,
) -> PaymentSettlement:
    variance = collected_amount_zar - expected_amount_zar
    status = PaymentSettlementStatus.MATCHED if variance == 0 else PaymentSettlementStatus.VARIANCE

    settlement = PaymentSettlement(
        provider=provider,
        settlement_date=settlement_date,
        expected_amount_zar=expected_amount_zar,
        collected_amount_zar=collected_amount_zar,
        variance_zar=variance,
        transaction_count=transaction_count,
        status=status,
        notes=notes,
        raw_data=raw_data,
        recorded_by=recorded_by,
    )
    db.add(settlement)

    log_operations_action(
        db,
        category=OperationsAuditCategory.SETTLEMENT,
        action="payment_settlement_recorded",
        entity_type="payment_settlement",
        user_id=recorded_by,
        details={"provider": provider, "variance_zar": str(variance)},
        ip_address=ip_address,
    )
    db.flush()
    return settlement


def reconcile_provider_from_references(
    db: Session,
    *,
    provider: str,
    settlement_date: date,
    recorded_by: int,
    ip_address: str | None = None,
) -> PaymentSettlement:
    refs = (
        db.query(PaymentReference)
        .filter(
            PaymentReference.provider == provider,
            PaymentReference.status.in_([PaymentReferenceStatus.PAID, PaymentReferenceStatus.VERIFIED]),
        )
        .all()
    )
    collected = sum((r.amount for r in refs), Decimal("0"))
    return record_payment_settlement(
        db,
        provider=provider,
        settlement_date=settlement_date,
        expected_amount_zar=collected,
        collected_amount_zar=collected,
        transaction_count=len(refs),
        recorded_by=recorded_by,
        notes="Auto-reconciled from payment references",
        ip_address=ip_address,
    )
