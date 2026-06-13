"""WhatsApp self-service bot with conversation logging."""

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.beneficiary import Beneficiary
from app.models.enums import OperationsAuditCategory
from app.models.payment_reference import PaymentReference
from app.models.transfer import Transfer
from app.models.whatsapp_conversation import WhatsAppConversationLog
from app.services.operations_audit import log_operations_action
from app.whatsapp.base import WhatsAppInboundMessage, WhatsAppOutboundMessage
from app.whatsapp.registry import get_whatsapp_bot_transport

MENU = (
    "TransAfrik Remit WhatsApp\n\n"
    "Reply with a number:\n"
    "1. Track Transfer\n"
    "2. View Voucher\n"
    "3. Beneficiary Status\n"
    "4. Payment Instructions\n"
    "5. Contact Support"
)


def _log_conversation(
    db: Session,
    *,
    provider_code: str,
    phone: str,
    direction: str,
    menu_option: str | None,
    message_body: str | None,
    response_body: str | None,
    user_id: int | None = None,
    transfer_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        WhatsAppConversationLog(
            provider_code=provider_code,
            phone_number=phone,
            direction=direction,
            menu_option=menu_option,
            message_body=message_body,
            response_body=response_body,
            user_id=user_id,
            transfer_id=transfer_id,
            metadata_json=metadata,
        )
    )


def _track_transfer(db: Session, phone: str, body: str) -> str:
    ref = body.strip().upper()
    transfer = db.query(Transfer).filter(Transfer.reference == ref).first()
    if not transfer:
        return f"Transfer {ref} not found. Please check your reference and try again."
    return (
        f"Transfer {transfer.reference}\n"
        f"Status: {transfer.status}\n"
        f"Amount: R{transfer.send_amount_zar} → GHS {transfer.receive_amount_ghs}"
    )


def _view_voucher(db: Session, phone: str, body: str) -> str:
    ref = body.strip().upper()
    transfer = db.query(Transfer).filter(Transfer.reference == ref).first()
    if not transfer:
        return "Transfer not found."
    payment_ref = (
        db.query(PaymentReference)
        .filter(PaymentReference.transfer_id == transfer.id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    if not payment_ref:
        return f"No voucher for {ref}. Status: {transfer.status}"
    return (
        f"Voucher for {ref}\n"
        f"Reference: {payment_ref.reference_number}\n"
        f"Voucher: {payment_ref.voucher_number or 'N/A'}\n"
        f"Status: {payment_ref.status}"
    )


def _beneficiary_status(db: Session, phone: str, body: str) -> str:
    try:
        beneficiary_id = int(body.strip())
    except ValueError:
        return "Please reply with your beneficiary ID number."
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not beneficiary:
        return "Beneficiary not found."
    return f"Beneficiary: {beneficiary.full_name}\nStatus: {beneficiary.status}\nType: {beneficiary.beneficiary_type}"


def _payment_instructions(db: Session, phone: str, body: str) -> str:
    ref = body.strip().upper()
    transfer = db.query(Transfer).filter(Transfer.reference == ref).first()
    if not transfer:
        return "Transfer not found."
    payment_ref = (
        db.query(PaymentReference)
        .filter(PaymentReference.transfer_id == transfer.id)
        .order_by(PaymentReference.created_at.desc())
        .first()
    )
    if payment_ref and payment_ref.banking_instructions:
        lines = [f"Payment instructions for {ref}:"]
        for k, v in payment_ref.banking_instructions.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)
    return (
        f"Pay at any Pay@, EasyPay, Kazang, Flash, Shoprite or Pick n Pay outlet.\n"
        f"Use reference: {payment_ref.reference_number if payment_ref else ref}"
    )


def _contact_support() -> str:
    return (
        "TransAfrik Support\n"
        "Email: support@transafrik.co.za\n"
        "Hours: Mon–Fri 08:00–17:00 SAST\n"
        "Or log in at transafrik.co.za/dashboard/support"
    )


def handle_inbound_message(
    db: Session,
    inbound: WhatsAppInboundMessage,
    *,
    transport_code: str | None = None,
) -> str:
    settings = get_settings()
    transport_code = transport_code or getattr(settings, "whatsapp_bot_provider", "twilio")
    transport = get_whatsapp_bot_transport(transport_code, {})

    body = (inbound.body or "").strip()
    response = MENU
    menu_option = None

    if body in ("hi", "hello", "menu", "start", ""):
        response = MENU
    elif body == "1":
        menu_option = "track_transfer"
        response = "Please reply with your transfer reference (e.g. TA-2024-XXXX)."
    elif body == "2":
        menu_option = "view_voucher"
        response = "Please reply with your transfer reference to view your voucher."
    elif body == "3":
        menu_option = "beneficiary_status"
        response = "Please reply with your beneficiary ID."
    elif body == "4":
        menu_option = "payment_instructions"
        response = "Please reply with your transfer reference for payment instructions."
    elif body == "5":
        menu_option = "contact_support"
        response = _contact_support()
    elif body.upper().startswith("TA-"):
        response = _track_transfer(db, inbound.from_number, body)
        menu_option = "track_transfer"
    else:
        response = _track_transfer(db, inbound.from_number, body) if len(body) > 5 else MENU

    _log_conversation(
        db,
        provider_code=transport.provider_code,
        phone=inbound.from_number,
        direction="inbound",
        menu_option=menu_option,
        message_body=inbound.body,
        response_body=response,
    )
    log_operations_action(
        db,
        category=OperationsAuditCategory.WHATSAPP,
        action="whatsapp_bot_message",
        entity_type="whatsapp_conversation",
        details={"from": inbound.from_number, "menu": menu_option},
    )

    outbound = WhatsAppOutboundMessage(to_number=inbound.from_number, body=response)
    transport.send_message(outbound)
    return response


def process_webhook(db: Session, transport_code: str, payload: dict) -> dict:
    transport = get_whatsapp_bot_transport(transport_code, {})
    inbound = transport.parse_webhook(payload)
    if not inbound:
        inbound = WhatsAppInboundMessage(
            from_number=payload.get("From", payload.get("from", "unknown")),
            body=payload.get("Body", payload.get("body", payload.get("text", ""))),
        )
    response = handle_inbound_message(db, inbound, transport_code=transport_code)
    return {"success": True, "response": response}
