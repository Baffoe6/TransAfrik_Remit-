from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.services.referral_program_service import get_customer_referral_dashboard

router = APIRouter(prefix="/referrals", tags=["Customer Referrals"])
CustomerUser = Annotated[User, Depends(require_roles(UserRole.CUSTOMER, UserRole.ADMIN))]


@router.get("/dashboard")
def referral_dashboard(user: CustomerUser, db: Annotated[Session, Depends(get_db)]):
    return get_customer_referral_dashboard(db, user.id)
