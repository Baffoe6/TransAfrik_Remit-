import secrets
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import AgentCommission, AgentProfile, AgentReferral
from app.models.enums import AgentCommissionStatus, OperationsAuditCategory, ReferralType, TransferStatus
from app.models.transfer import Transfer
from app.models.user import User
from app.services.operations_audit import log_operations_action
from app.services.wallet_service import get_or_create_wallet_profile


def create_agent_profile(db: Session, *, user_id: int, display_name: str, region: str | None, commission_rate: Decimal) -> AgentProfile:
    code = f"AG{secrets.token_hex(3).upper()}"
    agent = AgentProfile(
        user_id=user_id,
        agent_code=code,
        display_name=display_name,
        region=region,
        commission_rate=commission_rate,
    )
    db.add(agent)
    db.flush()
    return agent


def record_customer_referral(db: Session, *, agent: AgentProfile, customer_user_id: int, referral_code: str) -> AgentReferral:
    referral = AgentReferral(
        agent_id=agent.id,
        customer_user_id=customer_user_id,
        referral_type=ReferralType.CUSTOMER,
        referral_code_used=referral_code,
    )
    db.add(referral)
    wallet = get_or_create_wallet_profile(db, customer_user_id)
    wallet.referred_by_agent_id = agent.id
    db.flush()
    return referral


def record_transfer_referral(db: Session, *, agent: AgentProfile, transfer: Transfer) -> AgentReferral:
    referral = AgentReferral(
        agent_id=agent.id,
        transfer_id=transfer.id,
        customer_user_id=transfer.user_id,
        referral_type=ReferralType.TRANSFER,
        referral_code_used=agent.agent_code,
    )
    db.add(referral)
    db.flush()
    return referral


def calculate_commission(db: Session, *, agent: AgentProfile, transfer: Transfer) -> AgentCommission:
    amount = (transfer.send_amount_zar * agent.commission_rate / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    commission = AgentCommission(
        agent_id=agent.id,
        transfer_id=transfer.id,
        transfer_amount_zar=transfer.send_amount_zar,
        commission_rate=agent.commission_rate,
        commission_amount_zar=amount,
        status=AgentCommissionStatus.PENDING,
    )
    db.add(commission)
    log_operations_action(
        db,
        category=OperationsAuditCategory.AGENT,
        action="commission_calculated",
        entity_type="agent_commission",
        details={"agent_code": agent.agent_code, "transfer_id": transfer.id, "amount_zar": str(amount)},
    )
    db.flush()
    return commission


def get_agent_dashboard(db: Session, agent: AgentProfile) -> dict:
    referrals = db.query(func.count(AgentReferral.id)).filter(AgentReferral.agent_id == agent.id).scalar() or 0
    customer_refs = (
        db.query(func.count(AgentReferral.id))
        .filter(AgentReferral.agent_id == agent.id, AgentReferral.referral_type == ReferralType.CUSTOMER)
        .scalar() or 0
    )
    transfer_refs = (
        db.query(func.count(AgentReferral.id))
        .filter(AgentReferral.agent_id == agent.id, AgentReferral.referral_type == ReferralType.TRANSFER)
        .scalar() or 0
    )
    pending_commission = (
        db.query(func.coalesce(func.sum(AgentCommission.commission_amount_zar), 0))
        .filter(AgentCommission.agent_id == agent.id, AgentCommission.status == AgentCommissionStatus.PENDING)
        .scalar()
    )
    paid_commission = (
        db.query(func.coalesce(func.sum(AgentCommission.commission_amount_zar), 0))
        .filter(AgentCommission.agent_id == agent.id, AgentCommission.status == AgentCommissionStatus.PAID)
        .scalar()
    )
    return {
        "agent_code": agent.agent_code,
        "display_name": agent.display_name,
        "region": agent.region,
        "commission_rate": str(agent.commission_rate),
        "total_referrals": referrals,
        "customer_referrals": customer_refs,
        "transfer_referrals": transfer_refs,
        "pending_commission_zar": str(pending_commission),
        "paid_commission_zar": str(paid_commission),
    }
