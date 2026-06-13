from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import MukuruBatchStatus, MukuruSettlementStatus


class MukuruBatch(Base):
    __tablename__ = "mukuru_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[MukuruBatchStatus] = mapped_column(String(30), default=MukuruBatchStatus.DRAFT, index=True)
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_format: Mapped[str] = mapped_column(String(10), default="csv")
    transfer_count: Mapped[int] = mapped_column(Integer, default=0)
    total_amount_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_amount_ghs: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reconciled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    export_metadata: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["MukuruBatchItem"]] = relationship(
        "MukuruBatchItem", back_populates="batch", cascade="all, delete-orphan"
    )
    settlements: Mapped[list["MukuruSettlement"]] = relationship("MukuruSettlement", back_populates="batch")


class MukuruBatchItem(Base):
    __tablename__ = "mukuru_batch_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("mukuru_batches.id", ondelete="CASCADE"), index=True)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id", ondelete="RESTRICT"), index=True)
    amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_ghs: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    provider_reference: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    batch: Mapped["MukuruBatch"] = relationship("MukuruBatch", back_populates="items")


class MukuruSettlement(Base):
    __tablename__ = "mukuru_settlements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("mukuru_batches.id", ondelete="SET NULL"), index=True)
    settlement_reference: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_ghs: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    transfer_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[MukuruSettlementStatus] = mapped_column(String(30), default=MukuruSettlementStatus.PENDING, index=True)
    variance_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    batch: Mapped["MukuruBatch | None"] = relationship("MukuruBatch", back_populates="settlements")
