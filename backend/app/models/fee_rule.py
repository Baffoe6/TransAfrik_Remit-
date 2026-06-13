from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeeRule(Base):
    __tablename__ = "fee_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    min_amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    max_amount_zar: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    fee_type: Mapped[str] = mapped_column(String(20), default="flat")
    fee_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    destination_country: Mapped[str | None] = mapped_column(String(2), index=True)
    payment_method_id: Mapped[int | None] = mapped_column(ForeignKey("payment_methods.id", ondelete="SET NULL"))
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("providers.id", ondelete="SET NULL"))
    priority: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
