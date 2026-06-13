from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WaitlistLead(Base):
    __tablename__ = "waitlist_leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mobile: Mapped[str | None] = mapped_column(String(30))
    country_from: Mapped[str] = mapped_column(String(2), default="ZA")
    country_to: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    estimated_monthly_volume: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
