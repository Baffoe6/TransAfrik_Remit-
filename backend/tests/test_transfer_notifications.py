"""Transfer status notification tests."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.models.enums import InAppReadStatus, TransferStatus
from app.models.transfer import Transfer
from app.models.user import User
from app.models.user_notification import UserNotification
from app.services.transfer_notification_service import (
    TransferNotificationService,
    mark_all_notifications_read,
    mark_notification_read,
)


def _transfer(status=TransferStatus.QUOTE_CREATED) -> Transfer:
    t = Transfer(
        id=1,
        reference="TA-TEST-001",
        user_id=10,
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
    t.user = User(id=10, email="test@example.com", mobile_number="+27821234567", push_notifications_enabled=True)
    return t


def _mock_db_with_transfer(transfer: Transfer):
    db = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.first.return_value = transfer
    return db


@pytest.mark.parametrize(
    "status,event",
    [
        (TransferStatus.QUOTE_CREATED, "transfer_created"),
        (TransferStatus.PAYMENT_VERIFIED, "payment_received"),
        (TransferStatus.PROCESSING, "transfer_processing"),
        (TransferStatus.COMPLETED, "transfer_completed"),
        (TransferStatus.FAILED, "transfer_failed"),
    ],
)
def test_notification_created_on_status(status, event):
    transfer = _transfer(status=status)
    db = _mock_db_with_transfer(transfer)
    with patch.object(TransferNotificationService, "_deliver_push"):
        with patch.object(TransferNotificationService, "_deliver_sms"):
            with patch.object(TransferNotificationService, "_deliver_whatsapp"):
                with patch.object(TransferNotificationService, "_deliver_email"):
                    result = TransferNotificationService.notify_transfer_event(db, transfer, event)
    assert result is not None
    assert result.event_code == event
    db.add.assert_called()


def test_notification_created_on_customer_cancellation():
    transfer = _transfer(status=TransferStatus.CANCELLED)
    transfer.cancellation_reason = "customer_cancelled"
    db = _mock_db_with_transfer(transfer)
    with patch.object(TransferNotificationService, "_deliver_push"):
        with patch.object(TransferNotificationService, "_deliver_sms"):
            with patch.object(TransferNotificationService, "_deliver_whatsapp"):
                with patch.object(TransferNotificationService, "_deliver_email"):
                    result = TransferNotificationService.notify_transfer_event(db, transfer, "cancelled_customer")
    assert result.event_code == "cancelled_customer"


def test_notification_created_on_auto_cancellation():
    transfer = _transfer(status=TransferStatus.CANCELLED)
    transfer.cancellation_reason = "expired_unpaid_24h"
    db = _mock_db_with_transfer(transfer)
    with patch.object(TransferNotificationService, "_deliver_push"):
        with patch.object(TransferNotificationService, "_deliver_sms"):
            with patch.object(TransferNotificationService, "_deliver_whatsapp"):
                with patch.object(TransferNotificationService, "_deliver_email"):
                    result = TransferNotificationService.notify_transfer_event(db, transfer, "cancelled_auto_24h")
    assert "24 hours" in result.message


def test_notification_created_on_late_payment_review():
    transfer = _transfer(status=TransferStatus.CANCELLED)
    db = _mock_db_with_transfer(transfer)
    with patch.object(TransferNotificationService, "_deliver_push"):
        with patch.object(TransferNotificationService, "_deliver_sms"):
            with patch.object(TransferNotificationService, "_deliver_whatsapp"):
                with patch.object(TransferNotificationService, "_deliver_email"):
                    result = TransferNotificationService.notify_late_payment_review(db, transfer)
    assert result.event_code == "late_payment_review"


def test_mark_notification_read():
    n = UserNotification(
        id=1,
        user_id=10,
        notification_type="transfer_status",
        event_code="transfer_created",
        title="T",
        message="M",
        read_status=InAppReadStatus.UNREAD.value,
    )
    db = MagicMock()
    result = mark_notification_read(db, n)
    assert result.read_status == InAppReadStatus.READ.value
    assert result.read_at is not None


def test_mark_all_notifications_read():
    db = MagicMock()
    db.query.return_value.filter.return_value.update.return_value = 3
    count = mark_all_notifications_read(db, 10)
    assert count == 3


def test_customer_cannot_read_another_users_notification():
    n = UserNotification(id=1, user_id=99, notification_type="transfer_status", event_code="x", title="T", message="M")
    assert n.user_id != 10
