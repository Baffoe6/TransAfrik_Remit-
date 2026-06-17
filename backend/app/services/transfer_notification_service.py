"""Transfer status notifications — in-app inbox and multi-channel delivery."""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session, joinedload

from app.models.enums import (
    CancellationReason,
    InAppNotificationType,
    InAppReadStatus,
    NotificationDeliveryChannel,
    NotificationDeliveryStatus,
    TransferStatus,
)
from app.models.transfer import Transfer
from app.models.user import User
from app.models.user_notification import NotificationDelivery, UserNotification
from app.notifications.registry import get_email_provider, get_sms_provider, get_whatsapp_provider

logger = logging.getLogger(__name__)

TRANSFER_EVENT_COPY: dict[str, tuple[str, str]] = {
    "transfer_created": (
        "Transfer created",
        "Your transfer has been created. Please complete payment within 24 hours.",
    ),
    "awaiting_payment": (
        "Awaiting payment",
        "Your transfer is awaiting payment. Complete payment to continue processing.",
    ),
    "payment_received": (
        "Payment received",
        "We have received your payment. Your transfer is now being processed.",
    ),
    "transfer_processing": (
        "Transfer processing",
        "Your transfer is being processed. We will notify you once it is sent to the recipient.",
    ),
    "payout_initiated": (
        "Payout initiated",
        "Your transfer has been sent for payout to your recipient.",
    ),
    "transfer_completed": (
        "Transfer completed",
        "Your transfer has been completed successfully.",
    ),
    "transfer_failed": (
        "Transfer failed",
        "Your transfer could not be completed. Please contact support or try again.",
    ),
    "cancelled_customer": (
        "Transfer cancelled",
        "Your unpaid transfer has been cancelled.",
    ),
    "cancelled_auto_24h": (
        "Transfer cancelled",
        "Your transfer was cancelled because payment was not received within 24 hours.",
    ),
    "late_payment_review": (
        "Payment under review",
        "We received payment after the transfer was cancelled. Our support team is reviewing it.",
    ),
}

CRITICAL_SMS_WHATSAPP_EVENTS = frozenset({
    "payment_received",
    "transfer_completed",
    "transfer_failed",
    "late_payment_review",
})

STATUS_TO_EVENT: dict[TransferStatus, str] = {
    TransferStatus.QUOTE_CREATED: "transfer_created",
    TransferStatus.DRAFT: "transfer_created",
    TransferStatus.AWAITING_PAYMENT: "awaiting_payment",
    TransferStatus.PAYMENT_PENDING: "awaiting_payment",
    TransferStatus.CHECKOUT_CREATED: "awaiting_payment",
    TransferStatus.PAYMENT_PENDING_VERIFICATION: "payment_received",
    TransferStatus.PAYMENT_VERIFIED: "payment_received",
    TransferStatus.READY_FOR_PROCESSING: "transfer_processing",
    TransferStatus.SUBMITTED_TO_MUKURU: "transfer_processing",
    TransferStatus.COMPLIANCE_REVIEW: "transfer_processing",
    TransferStatus.PROCESSING: "transfer_processing",
    TransferStatus.PAYOUT_PENDING: "payout_initiated",
    TransferStatus.COMPLETED: "transfer_completed",
    TransferStatus.FAILED: "transfer_failed",
}


def resolve_event_code(transfer: Transfer, status: TransferStatus | None = None) -> str | None:
    status = status or transfer.status
    if status == TransferStatus.CANCELLED:
        reason = transfer.cancellation_reason or ""
        if reason == CancellationReason.CUSTOMER_CANCELLED.value:
            return "cancelled_customer"
        if reason == CancellationReason.EXPIRED_UNPAID_24H.value:
            return "cancelled_auto_24h"
        return "cancelled_customer"
    return STATUS_TO_EVENT.get(status)


class TransferNotificationService:
    @staticmethod
    def notify_transfer_event(
        db: Session,
        transfer: Transfer,
        event_code: str,
        *,
        user: User | None = None,
    ) -> UserNotification | None:
        copy = TRANSFER_EVENT_COPY.get(event_code)
        if not copy:
            logger.warning("Unknown transfer notification event: %s", event_code)
            return None

        loaded = TransferNotificationService._load_transfer(db, transfer, user)
        if not loaded or not loaded.user:
            return None

        title, message = copy
        notification = UserNotification(
            user_id=loaded.user.id,
            transfer_id=loaded.id,
            notification_type=InAppNotificationType.TRANSFER_STATUS.value,
            event_code=event_code,
            title=title,
            message=message,
            transfer_reference=loaded.reference,
            read_status=InAppReadStatus.UNREAD.value,
        )
        db.add(notification)
        db.flush()

        TransferNotificationService._record_delivery(
            db,
            notification,
            NotificationDeliveryChannel.IN_APP,
            NotificationDeliveryStatus.SENT,
            recipient=str(loaded.user.id),
        )

        TransferNotificationService._deliver_push(db, notification, loaded.user)
        if event_code in CRITICAL_SMS_WHATSAPP_EVENTS:
            TransferNotificationService._deliver_sms(db, notification, loaded.user, message)
            TransferNotificationService._deliver_whatsapp(db, notification, loaded.user, message)
        TransferNotificationService._deliver_email(db, notification, loaded.user, title, message)

        db.flush()
        return notification

    @staticmethod
    def notify_status_change(db: Session, transfer: Transfer) -> UserNotification | None:
        event_code = resolve_event_code(transfer)
        if not event_code:
            return None
        return TransferNotificationService.notify_transfer_event(db, transfer, event_code)

    @staticmethod
    def notify_late_payment_review(db: Session, transfer: Transfer) -> UserNotification | None:
        return TransferNotificationService.notify_transfer_event(db, transfer, "late_payment_review")

    @staticmethod
    def _load_transfer(db: Session, transfer: Transfer, user: User | None) -> Transfer | None:
        if user and transfer.user:
            return transfer
        return (
            db.query(Transfer)
            .options(
                joinedload(Transfer.user).joinedload(User.profile),
                joinedload(Transfer.beneficiary),
            )
            .filter(Transfer.id == transfer.id)
            .first()
        )

    @staticmethod
    def _record_delivery(
        db: Session,
        notification: UserNotification,
        channel: NotificationDeliveryChannel,
        status: NotificationDeliveryStatus,
        *,
        recipient: str | None = None,
        provider_response: dict | None = None,
        error_message: str | None = None,
    ) -> NotificationDelivery:
        delivery = NotificationDelivery(
            notification_id=notification.id,
            channel=channel.value,
            status=status.value,
            recipient=recipient,
            provider_response=provider_response,
            error_message=error_message,
        )
        db.add(delivery)
        db.flush()
        return delivery

    @staticmethod
    def _deliver_push(db: Session, notification: UserNotification, user: User) -> None:
        if not user.push_notifications_enabled or not user.push_token:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.PUSH,
                NotificationDeliveryStatus.SKIPPED,
                recipient=user.push_token,
                error_message="Push not enabled or no token",
            )
            return
        try:
            # Expo push / FCM integration point — log success for now
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.PUSH,
                NotificationDeliveryStatus.SENT,
                recipient=user.push_token,
                provider_response={"queued": True},
            )
        except Exception as exc:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.PUSH,
                NotificationDeliveryStatus.FAILED,
                recipient=user.push_token,
                error_message=str(exc),
            )

    @staticmethod
    def _deliver_sms(db: Session, notification: UserNotification, user: User, body: str) -> None:
        if not user.mobile_number:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.SMS,
                NotificationDeliveryStatus.SKIPPED,
                error_message="No mobile number",
            )
            return
        try:
            result = get_sms_provider().send_sms(user.mobile_number, body)
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.SMS,
                NotificationDeliveryStatus.SENT if result.success else NotificationDeliveryStatus.FAILED,
                recipient=user.mobile_number,
                provider_response=result.raw_response,
                error_message=None if result.success else result.message,
            )
        except Exception as exc:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.SMS,
                NotificationDeliveryStatus.FAILED,
                recipient=user.mobile_number,
                error_message=str(exc),
            )

    @staticmethod
    def _deliver_whatsapp(db: Session, notification: UserNotification, user: User, body: str) -> None:
        if not user.mobile_number:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.WHATSAPP,
                NotificationDeliveryStatus.SKIPPED,
                error_message="No mobile number",
            )
            return
        try:
            result = get_whatsapp_provider().send_message(user.mobile_number, body)
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.WHATSAPP,
                NotificationDeliveryStatus.SENT if result.success else NotificationDeliveryStatus.FAILED,
                recipient=user.mobile_number,
                provider_response=result.raw_response,
                error_message=None if result.success else result.message,
            )
        except Exception as exc:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.WHATSAPP,
                NotificationDeliveryStatus.FAILED,
                recipient=user.mobile_number,
                error_message=str(exc),
            )

    @staticmethod
    def _deliver_email(
        db: Session,
        notification: UserNotification,
        user: User,
        subject: str,
        body: str,
    ) -> None:
        if not user.email:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.EMAIL,
                NotificationDeliveryStatus.SKIPPED,
                error_message="No email on file",
            )
            return
        try:
            result = get_email_provider().send_email(user.email, f"TransAfrik: {subject}", body)
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.EMAIL,
                NotificationDeliveryStatus.SENT if result.success else NotificationDeliveryStatus.FAILED,
                recipient=user.email,
                provider_response=result.raw_response,
                error_message=None if result.success else result.message,
            )
        except Exception as exc:
            TransferNotificationService._record_delivery(
                db,
                notification,
                NotificationDeliveryChannel.EMAIL,
                NotificationDeliveryStatus.FAILED,
                recipient=user.email,
                error_message=str(exc),
            )


def mark_notification_read(db: Session, notification: UserNotification) -> UserNotification:
    if notification.read_status != InAppReadStatus.READ.value:
        notification.read_status = InAppReadStatus.READ.value
        notification.read_at = datetime.now(UTC)
        db.flush()
    return notification


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    now = datetime.now(UTC)
    updated = (
        db.query(UserNotification)
        .filter(
            UserNotification.user_id == user_id,
            UserNotification.read_status == InAppReadStatus.UNREAD.value,
        )
        .update({UserNotification.read_status: InAppReadStatus.READ.value, UserNotification.read_at: now})
    )
    db.flush()
    return updated
