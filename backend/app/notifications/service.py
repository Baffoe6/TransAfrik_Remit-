from string import Formatter

from sqlalchemy.orm import Session

from app.models.enums import NotificationChannel, NotificationStatus
from app.models.notification import NotificationLog, NotificationTemplate
from app.models.transfer import Transfer
from app.models.user import User
from app.notifications.registry import get_email_provider, get_sms_provider, get_whatsapp_provider


def render_template(template: str, context: dict) -> str:
  safe = Formatter()
  return safe.vformat(template, (), {k: str(v) if v is not None else "" for k, v in context.items()})


def send_notification(
    db: Session,
    *,
    template_code: str,
    channel: NotificationChannel,
    recipient: str,
    context: dict,
    user_id: int | None = None,
    transfer_id: int | None = None,
) -> NotificationLog:
    template = (
        db.query(NotificationTemplate)
        .filter(
            NotificationTemplate.code == template_code,
            NotificationTemplate.channel == channel,
            NotificationTemplate.is_active.is_(True),
        )
        .first()
    )
    if not template:
        raise ValueError(f"Template not found: {template_code}/{channel.value}")

    subject = render_template(template.subject, context) if template.subject else None
    body = render_template(template.body_template, context)

    if channel == NotificationChannel.EMAIL:
        result = get_email_provider().send_email(recipient, subject or "TransAfrik Remit", body)
    elif channel == NotificationChannel.WHATSAPP:
        result = get_whatsapp_provider().send_message(recipient, body)
    else:
        result = get_sms_provider().send_sms(recipient, body)

    log = NotificationLog(
        user_id=user_id,
        transfer_id=transfer_id,
        template_code=template_code,
        channel=channel,
        recipient=recipient,
        subject=subject,
        body=body,
        status=NotificationStatus.SENT if result.success else NotificationStatus.FAILED,
        provider_response=result.raw_response,
    )
    db.add(log)
    db.flush()
    return log


def notify_transfer_lifecycle(
    db: Session,
    transfer: Transfer,
    event: str,
    user: User,
    extra: dict | None = None,
) -> list[NotificationLog]:
    """Send notifications for transfer lifecycle events."""
    profile_name = "Customer"
    if transfer.user and transfer.user.profile:
        profile_name = f"{transfer.user.profile.first_name} {transfer.user.profile.last_name}"

    context = {
        "customer_name": profile_name,
        "reference": transfer.reference,
        "amount_zar": str(transfer.send_amount_zar),
        "total_zar": str(transfer.total_amount_zar),
        "receive_ghs": str(transfer.receive_amount_ghs),
        "status": transfer.status.value if hasattr(transfer.status, "value") else transfer.status,
        "beneficiary_name": transfer.beneficiary.full_name if transfer.beneficiary else "",
        "payment_reference": "",
        "reason": transfer.rejection_reason or "",
        **(extra or {}),
    }

    if transfer.payment_references:
        context["payment_reference"] = transfer.payment_references[0].reference_number

    logs: list[NotificationLog] = []
    templates = (
        db.query(NotificationTemplate)
        .filter(NotificationTemplate.code == event, NotificationTemplate.is_active.is_(True))
        .all()
    )
    for tmpl in templates:
        if tmpl.channel == NotificationChannel.EMAIL:
            recipient = user.email
        elif tmpl.channel in (NotificationChannel.SMS, NotificationChannel.WHATSAPP):
            recipient = user.mobile_number or ""
        else:
            recipient = user.mobile_number or ""
        if not recipient:
            continue
        try:
            logs.append(send_notification(
                db,
                template_code=event,
                channel=NotificationChannel(tmpl.channel),
                recipient=recipient,
                context=context,
                user_id=user.id,
                transfer_id=transfer.id,
            ))
        except ValueError:
            continue
    return logs
