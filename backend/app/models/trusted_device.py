"""Trusted device persistence for mobile-first auth."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrustedDevice(Base):
    __tablename__ = "trusted_devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_fingerprint_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    device_label: Mapped[str | None] = mapped_column(String(100))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trusted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
