from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.enums import SupportPriority
from app.models.user import User
from app.schemas.support import SupportTicketCreate, SupportTicketResponse
from app.services.support_ops_service import create_ticket_enhanced

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/tickets", response_model=SupportTicketResponse, status_code=201)
def create_ticket(
    data: SupportTicketCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    priority = SupportPriority(data.priority) if data.priority in [p.value for p in SupportPriority] else SupportPriority.NORMAL
    ticket = create_ticket_enhanced(
        db,
        user_id=current_user.id,
        subject=data.subject,
        message=data.message,
        priority=priority,
        transfer_id=data.transfer_id,
    )
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=list[SupportTicketResponse])
def list_tickets(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    from app.models.support_ticket import SupportTicket

    return (
        db.query(SupportTicket)
        .filter(SupportTicket.user_id == current_user.id)
        .order_by(SupportTicket.created_at.desc())
        .all()
    )
