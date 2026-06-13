from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.services.demo_mode_service import DEMO_WARNING, is_demo_mode
from app.services.pilot_service import get_pilot_dashboard

router = APIRouter(prefix="/pilot", tags=["Pilot"])
CustomerUser = Annotated[User, Depends(require_roles(UserRole.CUSTOMER, UserRole.ADMIN))]


@router.get("/dashboard")
def pilot_dashboard(user: CustomerUser, db: Annotated[Session, Depends(get_db)]):
    data = get_pilot_dashboard(db, user.id)
    if is_demo_mode(db):
        data["demo_warning"] = DEMO_WARNING
    return data
