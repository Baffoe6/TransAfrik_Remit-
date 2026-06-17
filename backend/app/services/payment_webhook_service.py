"""Process payment provider webhooks and update transfer state."""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.enums import OperationsAuditCategory, PaymentEventType, PaymentReferenceStatus, TransferStatus
from app.models.payment_method import PaymentMethod
from app.models.payment_reference import PaymentReference
from app.models.transfer import Transfer
from app.payment_providers.base import WebhookResult
from app.payment_providers.registry import get_payment_provider
from app.services.operations_audit import log_operations_action
from app.services.payment_collection import log_payment_event, mark_reference_paid
from app.services.transfer_cancellation_service import handle_late_payment_on_cancelled_transfer

logger = logging.getLogger(__name__)


def apply_payment_webhook(db: Session, provider_code: str, payload: dict) -> WebhookResult:
    provider = get_payment_provider(provider_code)
    result = provider.process_webhook(payload)

    if not result.success or not result.reference_number:
        return result

    payment_ref = (
        db.query(PaymentReference)
        .filter(PaymentReference.reference_number == result.reference_number)
        .first()
    )
    if not payment_ref:
        logger.warning("Webhook reference not found: %s", result.reference_number)
        return result

    transfer = db.query(Transfer).filter(Transfer.id == payment_ref.transfer_id).first()
    if not transfer:
        return result

    if result.status == "paid":
        if transfer.status == TransferStatus.CANCELLED:
            handle_late_payment_on_cancelled_transfer(
                db,
                transfer,
                payment_ref,
                provider_code=provider_code,
                payload=payload,
            )
            log_operations_action(
                db,
                category=OperationsAuditCategory.PROVIDER,
                action="late_payment_webhook_after_cancellation",
                entity_type="payment_reference",
                entity_id=payment_ref.id,
                details={
                    "provider": provider_code,
                    "reference": result.reference_number,
                    "transfer_id": transfer.id,
                },
            )
            db.flush()
            return result

        if payment_ref.status == PaymentReferenceStatus.AWAITING_PAYMENT:
            method = db.query(PaymentMethod).filter(PaymentMethod.id == payment_ref.payment_method_id).first()
            mark_reference_paid(
                db,
                payment_ref,
                transfer,
                requires_proof_upload=method.requires_proof_upload if method else False,
            )
            payment_ref.status = PaymentReferenceStatus.VERIFIED
            log_payment_event(
                db,
                transfer.id,
                PaymentEventType.WEBHOOK_RECEIVED,
                provider_reference=result.reference_number,
                raw_payload=payload,
                notes=f"Webhook payment confirmed via {provider_code}",
            )
            log_operations_action(
                db,
                category=OperationsAuditCategory.PROVIDER,
                action="payment_webhook_processed",
                entity_type="payment_reference",
                entity_id=payment_ref.id,
                details={"provider": provider_code, "reference": result.reference_number, "status": result.status},
            )
    elif result.status == "expired":
        payment_ref.status = PaymentReferenceStatus.EXPIRED
        log_payment_event(
            db,
            transfer.id,
            PaymentEventType.REFERENCE_EXPIRED,
            provider_reference=result.reference_number,
            raw_payload=payload,
        )

    db.flush()
    return result
