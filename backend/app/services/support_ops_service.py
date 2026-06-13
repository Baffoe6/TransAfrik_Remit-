"""Enhanced support operations: SLA, escalation, internal notes."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.enums import SupportPriority, SupportTicketStatus
from app.models.support_ops import SupportTicketNote
from app.models.support_ticket import SupportTicket

SLA_HOURS = {
    SupportPriority.LOW: 72,
    SupportPriority.NORMAL: 24,
    SupportPriority.HIGH: 8,
    SupportPriority.URGENT: 2,
}


def compute_sla_due(priority: SupportPriority) -> datetime:
    return datetime.now(UTC) + timedelta(hours=SLA_HOURS.get(priority, 24))


def create_ticket_enhanced(
    db: Session,
    *,
    user_id: int,
    subject: str,
    message: str,
    priority: SupportPriority = SupportPriority.NORMAL,
    transfer_id: int | None = None,
) -> SupportTicket:
    sla_hours = SLA_HOURS.get(priority, 24)
    ticket = SupportTicket(
        user_id=user_id,
        subject=subject,
        message=message,
        priority=priority,
        transfer_id=transfer_id,
        sla_hours=sla_hours,
        sla_due_at=compute_sla_due(priority),
    )
    db.add(ticket)
    db.flush()
    return ticket


def add_internal_note(db: Session, ticket_id: int, author_id: int, note: str) -> SupportTicketNote:
    entry = SupportTicketNote(ticket_id=ticket_id, author_id=author_id, note=note, is_internal=True)
    db.add(entry)
    db.flush()
    return entry


def escalate_ticket(db: Session, ticket: SupportTicket) -> SupportTicket:
    ticket.escalated = True
    ticket.priority = SupportPriority.URGENT
    ticket.sla_due_at = compute_sla_due(SupportPriority.URGENT)
    ticket.sla_hours = SLA_HOURS[SupportPriority.URGENT]
    if ticket.status == SupportTicketStatus.OPEN:
        ticket.status = SupportTicketStatus.IN_PROGRESS
    return ticket


def handoff_to_whatsapp(db: Session, ticket: SupportTicket) -> SupportTicket:
    ticket.whatsapp_handoff = True
    return ticket


def get_escalation_queue(db: Session) -> list[SupportTicket]:
    return (
        db.query(SupportTicket)
        .filter(
            SupportTicket.escalated.is_(True),
            SupportTicket.status.in_([SupportTicketStatus.OPEN, SupportTicketStatus.IN_PROGRESS]),
        )
        .order_by(SupportTicket.sla_due_at.asc())
        .all()
    )


def get_sla_breaches(db: Session) -> list[SupportTicket]:
    now = datetime.now(UTC)
    return (
        db.query(SupportTicket)
        .filter(
            SupportTicket.sla_due_at < now,
            SupportTicket.status.in_([SupportTicketStatus.OPEN, SupportTicketStatus.IN_PROGRESS]),
        )
        .order_by(SupportTicket.sla_due_at.asc())
        .all()
    )
