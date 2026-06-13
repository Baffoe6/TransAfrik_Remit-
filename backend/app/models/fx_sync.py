from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FxRateSnapshot(Base):
    __tablename__ = "fx_rate_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    base_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    effective_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    margin_applied: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class FxSyncRun(Base):
    __tablename__ = "fx_sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    pairs_synced: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
