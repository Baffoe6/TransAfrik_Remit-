from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TransferStatus


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    beneficiary_id: Mapped[int] = mapped_column(ForeignKey("beneficiaries.id", ondelete="RESTRICT"), index=True)
    payment_method_id: Mapped[int | None] = mapped_column(ForeignKey("payment_methods.id", ondelete="SET NULL"))
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("providers.id", ondelete="SET NULL"))
    provider_reference: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[TransferStatus] = mapped_column(String(30), default=TransferStatus.DRAFT, index=True)
    send_amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fee_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    receive_amount_ghs: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    aml_flags: Mapped[dict | None] = mapped_column(JSONB)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    compliance_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    compliance_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    batch_export_id: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="transfers", foreign_keys=[user_id])
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="transfers")
    payment_method: Mapped["PaymentMethod | None"] = relationship("PaymentMethod", back_populates="transfers")
    provider: Mapped["Provider | None"] = relationship("Provider", back_populates="transfers")
    status_history: Mapped[list["TransferStatusHistory"]] = relationship(
        "TransferStatusHistory", back_populates="transfer", cascade="all, delete-orphan"
    )
    payment_proofs: Mapped[list["PaymentProof"]] = relationship(
        "PaymentProof", back_populates="transfer", cascade="all, delete-orphan"
    )
    payment_references: Mapped[list["PaymentReference"]] = relationship(
        "PaymentReference", back_populates="transfer", cascade="all, delete-orphan"
    )
    payment_events: Mapped[list["PaymentEvent"]] = relationship(
        "PaymentEvent", back_populates="transfer", cascade="all, delete-orphan"
    )
    payment_verifications: Mapped[list["PaymentVerification"]] = relationship(
        "PaymentVerification", back_populates="transfer", cascade="all, delete-orphan"
    )
