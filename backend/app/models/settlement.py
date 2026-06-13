from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import PaymentSettlementStatus


class PaymentSettlement(Base):
    __tablename__ = "payment_settlements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expected_amount_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    collected_amount_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    variance_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PaymentSettlementStatus] = mapped_column(
        String(30), default=PaymentSettlementStatus.PENDING, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
