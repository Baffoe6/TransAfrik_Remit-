from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import EddStatus, SanctionsResult


class CustomerRiskProfile(Base):
    __tablename__ = "customer_risk_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    aml_flag_count: Mapped[int] = mapped_column(Integer, default=0)
    total_transfer_volume_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    transfer_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SanctionsScreening(Base):
    __tablename__ = "sanctions_screenings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id", ondelete="SET NULL"), index=True)
    screened_name: Mapped[str] = mapped_column(String(200), nullable=False)
    result: Mapped[SanctionsResult] = mapped_column(String(30), default=SanctionsResult.CLEAR)
    match_details: Mapped[dict | None] = mapped_column(JSONB)
    provider: Mapped[str] = mapped_column(String(50), default="internal_placeholder")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class EnhancedDueDiligenceCase(Base):
    __tablename__ = "enhanced_due_diligence_cases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id", ondelete="SET NULL"), index=True)
    status: Mapped[EddStatus] = mapped_column(String(20), default=EddStatus.OPEN, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    aml_flags: Mapped[dict | None] = mapped_column(JSONB)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
