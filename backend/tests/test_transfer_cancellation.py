"""Transfer cancellation tests."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.models.enums import CancellationReason, PaymentReferenceStatus, TransferStatus
from app.models.payment_reference import PaymentReference
from app.models.security_hardening import SecurityAlert
from app.models.transfer import Transfer
from app.services.payment_webhook_service import apply_payment_webhook
from app.services.transfer_cancellation_service import (
    cancel_expired_unpaid_transfers,
    cancel_transfer,
    can_customer_cancel,
    is_unpaid_cancellable,
)
from app.payment_providers.base import WebhookResult


def _transfer(
    *,
    status: TransferStatus = TransferStatus.AWAITING_PAYMENT,
    user_id: int = 1,
    created_at: datetime | None = None,
) -> Transfer:
    t = Transfer(
        id=1,
        reference="TA-TEST-001",
        user_id=user_id,
        beneficiary_id=1,
        status=status,
        send_amount_zar=Decimal("970"),
        fee_zar=Decimal("30"),
        exchange_rate=Decimal("0.615"),
        receive_amount_ghs=Decimal("596.55"),
        total_amount_zar=Decimal("1000"),
        risk_score=0,
        compliance_approved=False,
    )
    t.created_at = created_at or datetime.now(UTC)
    return t


def test_customer_can_cancel_unpaid_transfer():
    transfer = _transfer(status=TransferStatus.AWAITING_PAYMENT)
    assert can_customer_cancel(transfer)
    db = MagicMock()
    with patch("app.services.transfer_cancellation_service.record_status_change") as record:
        with patch("app.services.transfer_cancellation_service.log_payment_event"):
            with patch("app.services.transfer_cancellation_service._deactivate_payment_references", return_value=0):
                result = cancel_transfer(db, transfer, CancellationReason.CUSTOMER_CANCELLED, changed_by=1)
    assert result.cancellation_reason == CancellationReason.CUSTOMER_CANCELLED.value
    assert result.cancelled_at is not None
    record.assert_called_once()
    assert record.call_args[0][2] == TransferStatus.CANCELLED


def test_customer_cannot_cancel_paid_transfer():
    transfer = _transfer(status=TransferStatus.PAYMENT_VERIFIED)
    assert not can_customer_cancel(transfer)
    db = MagicMock()
    with pytest.raises(ValueError, match="cannot be cancelled"):
        cancel_transfer(db, transfer, CancellationReason.CUSTOMER_CANCELLED)


def test_cancel_is_idempotent():
    transfer = _transfer(status=TransferStatus.CANCELLED)
    transfer.cancellation_reason = CancellationReason.CUSTOMER_CANCELLED.value
    db = MagicMock()
    result = cancel_transfer(db, transfer, CancellationReason.CUSTOMER_CANCELLED)
    assert result.status == TransferStatus.CANCELLED
    db.query.assert_not_called()


def test_unpaid_statuses_include_required_values():
    for status in (
        TransferStatus.QUOTE_CREATED,
        TransferStatus.AWAITING_PAYMENT,
        TransferStatus.PAYMENT_PENDING,
        TransferStatus.CHECKOUT_CREATED,
    ):
        assert is_unpaid_cancellable(status)


def test_auto_cancel_old_unpaid_transfer():
    old = datetime.now(UTC) - timedelta(hours=25)
    transfer = _transfer(status=TransferStatus.AWAITING_PAYMENT, created_at=old)

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [transfer]

    with patch("app.services.transfer_cancellation_service.cancel_transfer") as mock_cancel:
        count = cancel_expired_unpaid_transfers(db, now=datetime.now(UTC))
    assert count == 1
    mock_cancel.assert_called_once()
    assert mock_cancel.call_args[0][2] == CancellationReason.EXPIRED_UNPAID_24H


def test_auto_cancel_skips_recent_unpaid():
    recent = datetime.now(UTC) - timedelta(hours=2)
    transfer = _transfer(status=TransferStatus.AWAITING_PAYMENT, created_at=recent)

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []

    with patch("app.services.transfer_cancellation_service.cancel_transfer") as mock_cancel:
        count = cancel_expired_unpaid_transfers(db, now=datetime.now(UTC))
    assert count == 0
    mock_cancel.assert_not_called()


def test_auto_cancel_skips_paid_transfer_not_in_query():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []

    with patch("app.services.transfer_cancellation_service.cancel_transfer") as mock_cancel:
        count = cancel_expired_unpaid_transfers(db)
    assert count == 0
    mock_cancel.assert_not_called()


def test_late_webhook_after_cancellation_creates_review():
    transfer = _transfer(status=TransferStatus.CANCELLED)
    transfer.cancellation_reason = CancellationReason.EXPIRED_UNPAID_24H.value
    payment_ref = PaymentReference(
        id=10,
        transfer_id=1,
        payment_method_id=1,
        provider="flutterwave",
        reference_number="FW-REF-123",
        amount=Decimal("1000"),
        status=PaymentReferenceStatus.AWAITING_PAYMENT,
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.first.side_effect = [payment_ref, transfer]

    mock_provider = MagicMock()
    mock_provider.process_webhook.return_value = WebhookResult(
        success=True,
        reference_number="FW-REF-123",
        status="paid",
    )

    with patch("app.services.payment_webhook_service.get_payment_provider", return_value=mock_provider):
        with patch("app.services.payment_webhook_service.mark_reference_paid") as mark_paid:
            with patch("app.services.payment_webhook_service.handle_late_payment_on_cancelled_transfer") as late:
                with patch("app.services.payment_webhook_service.log_operations_action"):
                    result = apply_payment_webhook(db, "flutterwave", {"event": "charge.completed"})

    late.assert_called_once()
    mark_paid.assert_not_called()
    assert result.success
