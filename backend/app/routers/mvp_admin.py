"""MVP admin: waitlist, compliance, operations, launch readiness."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.services.compliance_dashboard_service import export_compliance_csv, get_compliance_dashboard
from app.services.launch_readiness_service import get_launch_readiness
from app.services.operations_dashboard_service import get_operations_dashboard
from app.services.waitlist_service import export_waitlist_csv, list_waitlist_leads
from app.providers.partners.registry import get_partner_provider, list_partner_providers

router = APIRouter(prefix="/admin", tags=["Admin MVP"])
StaffUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.FOUNDER))]


@router.get("/waitlist")
def admin_waitlist(staff: StaffUser, db: Annotated[Session, Depends(get_db)], search: str | None = None):
    return list_waitlist_leads(db, search=search)


@router.get("/waitlist/export")
def admin_waitlist_export(staff: StaffUser, db: Annotated[Session, Depends(get_db)]):
    return PlainTextResponse(
        export_waitlist_csv(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=waitlist_leads.csv"},
    )


@router.get("/compliance/dashboard")
def admin_compliance_dashboard(staff: StaffUser, db: Annotated[Session, Depends(get_db)]):
    return get_compliance_dashboard(db)


@router.get("/compliance/export")
def admin_compliance_export(staff: StaffUser, db: Annotated[Session, Depends(get_db)]):
    return PlainTextResponse(
        export_compliance_csv(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=compliance_report.csv"},
    )


@router.get("/operations/dashboard")
def admin_operations_dashboard(staff: StaffUser, db: Annotated[Session, Depends(get_db)]):
    return get_operations_dashboard(db)


@router.get("/launch-readiness")
def admin_launch_readiness(staff: StaffUser, db: Annotated[Session, Depends(get_db)]):
    return get_launch_readiness(db)


@router.get("/partners")
def admin_partners(staff: StaffUser):
    return {"providers": list_partner_providers()}


@router.post("/partners/{code}/quote")
def admin_partner_quote(staff: StaffUser, code: str, amount: str = "1000", corridor: str = "ZA-GH"):
    from decimal import Decimal

    provider = get_partner_provider(code)
    quote = provider.quote(corridor=corridor, send_amount=Decimal(amount))
    return {
        "provider_code": quote.provider_code,
        "corridor": quote.corridor,
        "send_amount": str(quote.send_amount),
        "fee_amount": str(quote.fee_amount),
        "fx_rate": str(quote.fx_rate),
        "payout_amount": str(quote.payout_amount),
        "quote_reference": quote.quote_reference,
    }
