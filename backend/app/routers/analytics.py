from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.services.analytics import get_analytics_dashboard

router = APIRouter(prefix="/admin/analytics", tags=["Analytics"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER))]


@router.get("/dashboard")
def analytics_dashboard(admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    return get_analytics_dashboard(db)
