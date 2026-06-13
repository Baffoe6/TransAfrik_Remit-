"""Board & investor executive dashboard with growth trends."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import AgentProfile
from app.models.compliance import EnhancedDueDiligenceCase
from app.models.corridor import Corridor
from app.models.enums import EddStatus, TransferStatus
from app.models.referral_program import CustomerReferral
from app.models.transfer import Transfer
from app.models.user import User
from app.services.founder_dashboard import get_founder_executive_dashboard
from app.services.referral_program_service import get_founder_referral_metrics
from app.services.treasury_service import get_treasury_dashboard


def _monthly_series(db: Session, months: int = 6) -> list[dict]:
    series = []
    now = datetime.now(UTC)
    for i in range(months - 1, -1, -1):
        start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        volume = (
            db.query(func.coalesce(func.sum(Transfer.send_amount_zar), 0))
            .filter(Transfer.created_at >= start, Transfer.created_at < end)
            .scalar()
        )
        revenue = (
            db.query(func.coalesce(func.sum(Transfer.fee_zar), 0))
            .filter(
                Transfer.created_at >= start,
                Transfer.created_at < end,
                Transfer.status == TransferStatus.COMPLETED,
            )
            .scalar()
        )
        count = (
            db.query(func.count(Transfer.id))
            .filter(Transfer.created_at >= start, Transfer.created_at < end)
            .scalar()
        ) or 0
        series.append({
            "month": start.strftime("%Y-%m"),
            "volume_zar": str(volume),
            "revenue_zar": str(revenue),
            "transaction_count": count,
        })
    return series


def get_board_executive_dashboard(db: Session) -> dict:
    founder = get_founder_executive_dashboard(db)
    treasury = get_treasury_dashboard(db)
    referral_metrics = get_founder_referral_metrics(db)

    active_customers = db.query(func.count(User.id)).filter(User.role == "customer").scalar() or 0
    active_agents = db.query(func.count(AgentProfile.id)).filter(AgentProfile.is_active.is_(True)).scalar() or 0
    compliance_cases = (
        db.query(func.count(EnhancedDueDiligenceCase.id))
        .filter(EnhancedDueDiligenceCase.status.in_([EddStatus.OPEN, EddStatus.IN_REVIEW, EddStatus.ESCALATED]))
        .scalar()
        or 0
    )

    corridors = db.query(Corridor).order_by(Corridor.priority.desc()).limit(10).all()
    top_corridors = [(c.code, c.destination_country, c.priority) for c in corridors]

    provider_counts: dict[str, int] = {}
    corridors = db.query(Corridor).all()
    for c in corridors:
        provider_counts[c.provider_code] = provider_counts.get(c.provider_code, 0) + 1

    monthly = _monthly_series(db)

    return {
        "metrics": {
            "monthly_volume_zar": founder["collections"]["monthly_volume_zar"],
            "revenue_month_zar": founder["revenue"]["month_zar"],
            "active_customers": active_customers,
            "active_agents": active_agents,
            "compliance_cases": compliance_cases,
            "treasury_position_zar": treasury.get("available_balance_zar", treasury.get("funds_collected_today_zar")),
            "referral_growth": referral_metrics["total_referrals"],
            "referral_conversion_rate": referral_metrics["conversion_rate_percent"],
        },
        "top_corridors": [
            {"code": code, "destination": dest, "priority": cnt} for code, dest, cnt in top_corridors
        ],
        "top_providers": [
            {"provider": k, "corridor_count": v} for k, v in sorted(provider_counts.items(), key=lambda x: -x[1])
        ],
        "referral_program": referral_metrics,
        "charts": {
            "monthly_growth": monthly,
            "revenue_trend": [{"month": m["month"], "revenue_zar": m["revenue_zar"]} for m in monthly],
            "transaction_trend": [{"month": m["month"], "count": m["transaction_count"]} for m in monthly],
        },
        "founder_summary": founder,
    }
