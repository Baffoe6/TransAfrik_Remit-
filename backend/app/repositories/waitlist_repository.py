from sqlalchemy.orm import Session

from app.models.waitlist import WaitlistLead


class WaitlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, lead: WaitlistLead) -> WaitlistLead:
        self.db.add(lead)
        self.db.flush()
        return lead

    def get_by_email(self, email: str) -> WaitlistLead | None:
        return self.db.query(WaitlistLead).filter(WaitlistLead.email == email).first()

    def get_by_mobile(self, mobile: str) -> WaitlistLead | None:
        return self.db.query(WaitlistLead).filter(WaitlistLead.mobile == mobile).first()

    def list_leads(self, *, search: str | None = None, limit: int = 500) -> list[WaitlistLead]:
        q = self.db.query(WaitlistLead).order_by(WaitlistLead.created_at.desc())
        if search:
            term = f"%{search.lower()}%"
            q = q.filter(
                (WaitlistLead.email.ilike(term))
                | (WaitlistLead.first_name.ilike(term))
                | (WaitlistLead.last_name.ilike(term))
                | (WaitlistLead.mobile.ilike(term))
            )
        return q.limit(limit).all()

    def count(self) -> int:
        return self.db.query(WaitlistLead).count()
