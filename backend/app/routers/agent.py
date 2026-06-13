from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.agent import AgentCommission, AgentProfile, AgentReferral
from app.models.enums import UserRole
from app.models.user import User
from app.services.agent_service import get_agent_dashboard

router = APIRouter(prefix="/agent", tags=["Agent Portal"])
AgentUser = Annotated[User, Depends(require_roles(UserRole.AGENT, UserRole.ADMIN))]


def _get_agent(db: Session, user: User) -> AgentProfile:
    agent = db.query(AgentProfile).filter(AgentProfile.user_id == user.id, AgentProfile.is_active.is_(True)).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found")
    return agent


@router.get("/dashboard")
def agent_dashboard(agent_user: AgentUser, db: Annotated[Session, Depends(get_db)]):
    agent = _get_agent(db, agent_user)
    return get_agent_dashboard(db, agent)


@router.get("/commissions")
def agent_commissions(agent_user: AgentUser, db: Annotated[Session, Depends(get_db)]):
    agent = _get_agent(db, agent_user)
    rows = (
        db.query(AgentCommission)
        .filter(AgentCommission.agent_id == agent.id)
        .order_by(AgentCommission.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": c.id,
            "transfer_id": c.transfer_id,
            "transfer_amount_zar": str(c.transfer_amount_zar),
            "commission_amount_zar": str(c.commission_amount_zar),
            "status": c.status.value,
            "created_at": c.created_at.isoformat(),
        }
        for c in rows
    ]


@router.get("/referrals")
def agent_referrals(agent_user: AgentUser, db: Annotated[Session, Depends(get_db)]):
    agent = _get_agent(db, agent_user)
    rows = (
        db.query(AgentReferral)
        .filter(AgentReferral.agent_id == agent.id)
        .order_by(AgentReferral.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": r.id,
            "referral_type": r.referral_type.value,
            "customer_user_id": r.customer_user_id,
            "transfer_id": r.transfer_id,
            "referral_code_used": r.referral_code_used,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


class ReferralCodeLookup(BaseModel):
    referral_code: str = Field(min_length=4, max_length=20)


@router.get("/code/{referral_code}")
def validate_referral_code(referral_code: str, db: Annotated[Session, Depends(get_db)]):
    agent = db.query(AgentProfile).filter(AgentProfile.agent_code == referral_code, AgentProfile.is_active.is_(True)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    return {"agent_code": agent.agent_code, "display_name": agent.display_name, "valid": True}
