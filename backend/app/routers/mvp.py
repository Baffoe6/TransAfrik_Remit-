"""Public waitlist and customer MVP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.services.customer_dashboard_service import get_customer_dashboard
from app.services.waitlist_service import submit_waitlist_lead

router = APIRouter(tags=["MVP"])


class WaitlistJoinRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    mobile: str = Field(min_length=8, max_length=30)
    email: EmailStr | None = None
    country_from: str = "ZA"
    country_to: str = Field(min_length=2, max_length=2)
    estimated_monthly_volume: str | None = None


@router.post("/waitlist/join")
def join_waitlist(data: WaitlistJoinRequest, db: Annotated[Session, Depends(get_db)]):
    lead = submit_waitlist_lead(
        db,
        first_name=data.first_name,
        last_name=data.last_name,
        email=str(data.email) if data.email else None,
        mobile=data.mobile,
        country_from=data.country_from,
        country_to=data.country_to,
        estimated_monthly_volume=data.estimated_monthly_volume,
    )
    return {
        "joined": True,
        "id": lead.id,
        "message": "Thank you for joining the TransAfrik Remit waitlist.",
    }


@router.get("/dashboard/summary")
def customer_dashboard_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return get_customer_dashboard(db, current_user.id)
