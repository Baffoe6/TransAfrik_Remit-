"""Investor/partner demo mode — safe journeys with no real money."""

from sqlalchemy.orm import Session

from app.models.pilot import PilotSettings
from app.services.pilot_service import get_pilot_settings


DEMO_WARNING = (
    "DEMO MODE: No real money is processed. All transfers, payments, and provider "
    "interactions are simulated for demonstration purposes only."
)


def is_demo_mode(db: Session) -> bool:
    settings = get_pilot_settings(db)
    return settings.demo_mode_enabled


def get_demo_journeys() -> dict:
    return {
        "warning": DEMO_WARNING,
        "customer_journey": [
            {"step": 1, "action": "Login as customer@demo.co.za", "path": "/login"},
            {"step": 2, "action": "View pilot dashboard", "path": "/dashboard/pilot"},
            {"step": 3, "action": "Complete KYC", "path": "/dashboard/kyc"},
            {"step": 4, "action": "Add beneficiary", "path": "/dashboard/beneficiaries"},
            {"step": 5, "action": "Create transfer", "path": "/dashboard/transfers/new"},
            {"step": 6, "action": "Track transfer", "path": "/dashboard/transfers"},
        ],
        "admin_journey": [
            {"step": 1, "action": "Login as admin", "path": "/login"},
            {"step": 2, "action": "Review launch checklist", "path": "/admin/launch-checklist"},
            {"step": 3, "action": "Approve pilot customer", "path": "/admin/pilot"},
            {"step": 4, "action": "Verify payment", "path": "/admin/payments/verify"},
            {"step": 5, "action": "Export Mukuru batch", "path": "/admin/mukuru"},
        ],
        "agent_journey": [
            {"step": 1, "action": "Login as agent", "path": "/login"},
            {"step": 2, "action": "View agent dashboard", "path": "/agent"},
            {"step": 3, "action": "Review referrals", "path": "/agent/referrals"},
        ],
        "founder_journey": [
            {"step": 1, "action": "Login as founder", "path": "/login"},
            {"step": 2, "action": "Executive dashboard", "path": "/admin/founder"},
            {"step": 3, "action": "Board dashboard", "path": "/admin/board"},
        ],
    }


def enable_demo_mode(db: Session) -> PilotSettings:
    settings = get_pilot_settings(db)
    settings.demo_mode_enabled = True
    return settings


def disable_demo_mode(db: Session) -> PilotSettings:
    settings = get_pilot_settings(db)
    settings.demo_mode_enabled = False
    return settings
