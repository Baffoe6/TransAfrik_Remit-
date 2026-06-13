from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import AgentCommission, AgentProfile, AgentReferral
from app.models.enums import TransferStatus
from app.services.analytics import get_analytics_dashboard
from app.models.compliance import EnhancedDueDiligenceCase, CustomerRiskProfile
from app.models.enums import EddStatus
from app.services.treasury_service import get_treasury_dashboard
from app.services.settlement_service import get_settlement_dashboard
from app.services.referral_program_service import get_founder_referral_metrics


def get_founder_executive_dashboard(db: Session) -> dict:
    analytics = get_analytics_dashboard(db)
    treasury = get_treasury_dashboard(db)
    settlement = get_settlement_dashboard(db)

    open_edd = db.query(func.count(EnhancedDueDiligenceCase.id)).filter(
        EnhancedDueDiligenceCase.status.in_([EddStatus.OPEN, EddStatus.IN_REVIEW])
    ).scalar() or 0

    high_risk_customers = (
        db.query(func.count(CustomerRiskProfile.id)).filter(CustomerRiskProfile.risk_level == "high").scalar() or 0
    )

    active_agents = db.query(func.count(AgentProfile.id)).filter(AgentProfile.is_active.is_(True)).scalar() or 0
    total_referrals = db.query(func.count(AgentReferral.id)).scalar() or 0
    agent_commissions_pending = (
        db.query(func.coalesce(func.sum(AgentCommission.commission_amount_zar), 0))
        .filter(AgentCommission.status == "pending")
        .scalar()
    )

    top_agents = (
        db.query(AgentProfile.display_name, AgentProfile.agent_code, func.count(AgentReferral.id))
        .outerjoin(AgentReferral, AgentReferral.agent_id == AgentProfile.id)
        .group_by(AgentProfile.id)
        .order_by(func.count(AgentReferral.id).desc())
        .limit(5)
        .all()
    )

    customer_referrals = get_founder_referral_metrics(db)

    return {
        "collections": {
            "daily_volume_zar": analytics["daily_volume_zar"],
            "monthly_volume_zar": analytics["monthly_volume_zar"],
            "daily_revenue_zar": analytics["daily_revenue_zar"],
            "monthly_revenue_zar": analytics["monthly_revenue_zar"],
            "funds_collected_today_zar": treasury["funds_collected_today_zar"],
        },
        "transfers": {
            "by_status": analytics["transfers_by_status"],
            "by_country": analytics["transfers_by_country"],
            "by_payment_method": analytics["transfers_by_payment_method"],
            "completed_today": analytics["completed_today"],
        },
        "revenue": {
            "today_zar": treasury["revenue_today_zar"],
            "month_zar": treasury["revenue_month_zar"],
        },
        "compliance": {
            "open_edd_cases": open_edd,
            "high_risk_customers": high_risk_customers,
        },
        "treasury": treasury,
        "settlement_variance_zar": settlement["total_variance_zar"],
        "customer_referral_program": customer_referrals,
        "agent_performance": {
            "active_agents": active_agents,
            "total_referrals": total_referrals,
            "pending_commissions_zar": str(agent_commissions_pending),
            "top_agents": [
                {"name": name, "code": code, "referrals": count} for name, code, count in top_agents
            ],
        },
    }
