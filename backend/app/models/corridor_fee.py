from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CorridorFeeRule(Base):
    """Corridor-level fee configuration with tiered customer fees."""

    __tablename__ = "corridor_fee_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    corridor_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source_country: Mapped[str] = mapped_column(String(2), default="ZA")
    destination_country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_cost_pct: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("0"))
    provider_cost_flat_zar: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tiers: Mapped[list["CorridorFeeTier"]] = relationship(
        "CorridorFeeTier", back_populates="rule", cascade="all, delete-orphan", order_by="CorridorFeeTier.sort_order"
    )


class CorridorFeeTier(Base):
    """Amount band within a corridor fee rule."""

    __tablename__ = "corridor_fee_tiers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("corridor_fee_rules.id", ondelete="CASCADE"), index=True)
    min_amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_amount_zar: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    fee_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    label: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    rule: Mapped["CorridorFeeRule"] = relationship("CorridorFeeRule", back_populates="tiers")
