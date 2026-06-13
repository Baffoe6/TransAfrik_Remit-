import csv
import io

from sqlalchemy.orm import Session

from app.models.waitlist import WaitlistLead
from app.repositories.waitlist_repository import WaitlistRepository
from app.utils.phone import validate_phone_number


def submit_waitlist_lead(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str | None,
    mobile: str,
    country_from: str,
    country_to: str,
    estimated_monthly_volume: str | None,
) -> WaitlistLead:
    repo = WaitlistRepository(db)
    normalized_mobile = validate_phone_number(mobile)
    existing = repo.get_by_mobile(normalized_mobile)
    if existing:
        return existing
    if email:
        existing_email = repo.get_by_email(email.strip().lower())
        if existing_email:
            return existing_email
    lead = WaitlistLead(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.strip().lower() if email else None,
        mobile=normalized_mobile,
        country_from=country_from.upper(),
        country_to=country_to.upper(),
        estimated_monthly_volume=estimated_monthly_volume,
    )
    repo.create(lead)
    db.commit()
    db.refresh(lead)
    return lead


def list_waitlist_leads(db: Session, *, search: str | None = None) -> dict:
    repo = WaitlistRepository(db)
    leads = repo.list_leads(search=search)
    return {
        "count": repo.count(),
        "leads": [
            {
                "id": l.id,
                "first_name": l.first_name,
                "last_name": l.last_name,
                "email": l.email,
                "mobile": l.mobile,
                "country_from": l.country_from,
                "country_to": l.country_to,
                "estimated_monthly_volume": l.estimated_monthly_volume,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in leads
        ],
    }


def export_waitlist_csv(db: Session) -> str:
    repo = WaitlistRepository(db)
    leads = repo.list_leads(limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "first_name", "last_name", "mobile", "email",
        "country_from", "country_to", "estimated_monthly_volume", "created_at",
    ])
    for l in leads:
        writer.writerow([
            l.id, l.first_name, l.last_name, l.mobile or "",
            l.email or "",
            l.country_from, l.country_to, l.estimated_monthly_volume or "",
            l.created_at.isoformat() if l.created_at else "",
        ])
    return output.getvalue()
