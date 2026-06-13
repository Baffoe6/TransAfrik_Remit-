from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CustomerWalletProfile(Base):
    """Customer wallet profile — activity summary only, no stored funds."""

    __tablename__ = "customer_wallet_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    total_sent_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_fees_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    transfer_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_transfer_count: Mapped[int] = mapped_column(Integer, default=0)
    preferred_corridor: Mapped[str] = mapped_column(String(10), default="ZAR-GHS")
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    referred_by_agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent_profiles.id", ondelete="SET NULL"))
    last_transfer_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
