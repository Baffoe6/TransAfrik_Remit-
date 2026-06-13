from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.enums import OperationsAuditCategory
from app.models.user import User
from app.services.operations_audit import log_operations_action
from app.services.wallet_service import refresh_wallet_stats, wallet_profile_response

router = APIRouter(prefix="/wallet", tags=["Wallet Profile"])


@router.get("/profile")
def get_wallet_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = refresh_wallet_stats(db, current_user.id)
    log_operations_action(
        db,
        category=OperationsAuditCategory.WALLET,
        action="wallet_profile_viewed",
        entity_type="customer_wallet_profile",
        user_id=current_user.id,
        entity_id=profile.id,
    )
    db.commit()
    return wallet_profile_response(profile)
