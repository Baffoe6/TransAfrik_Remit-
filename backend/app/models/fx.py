from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import FxMarkupType, FxRateSourceType


class FxRateSource(Base):
    __tablename__ = "fx_rate_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[FxRateSourceType] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(default=0)
    config: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class FxMarkupRule(Base):
    __tablename__ = "fx_markup_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    from_currency: Mapped[str] = mapped_column(String(3), default="ZAR")
    to_currency: Mapped[str] = mapped_column(String(3), default="GHS")
    markup_type: Mapped[FxMarkupType] = mapped_column(String(20), default=FxMarkupType.PERCENTAGE)
    markup_value: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(default=0)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
