from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import CorridorStatus


class Corridor(Base):
    __tablename__ = "corridors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    source_country: Mapped[str] = mapped_column(String(2), default="ZA")
    destination_country: Mapped[str] = mapped_column(String(2), nullable=False)
    destination_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    provider_code: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[CorridorStatus] = mapped_column(String(20), default=CorridorStatus.ACTIVE)
    fee_rule_id: Mapped[int | None] = mapped_column(ForeignKey("fee_rules.id", ondelete="SET NULL"))
    fx_markup_rule_id: Mapped[int | None] = mapped_column(ForeignKey("fx_markup_rules.id", ondelete="SET NULL"))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CorridorProviderRoute(Base):
    """Alternative provider routes for a corridor (cost/priority-based selection)."""

    __tablename__ = "corridor_provider_routes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    corridor_id: Mapped[int] = mapped_column(ForeignKey("corridors.id", ondelete="CASCADE"), index=True)
    provider_code: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    cost_score: Mapped[int] = mapped_column(Integer, default=100)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
