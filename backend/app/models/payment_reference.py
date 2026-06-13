from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import PaymentReferenceStatus


class PaymentReference(Base):
    __tablename__ = "payment_references"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id", ondelete="CASCADE"), index=True)
    payment_method_id: Mapped[int] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    voucher_number: Mapped[str | None] = mapped_column(String(50))
    barcode_data: Mapped[str | None] = mapped_column(String(500))
    qr_data: Mapped[str | None] = mapped_column(String(1000))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="ZAR")
    expiry_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[PaymentReferenceStatus] = mapped_column(
        String(30), default=PaymentReferenceStatus.AWAITING_PAYMENT, index=True
    )
    banking_instructions: Mapped[dict | None] = mapped_column(JSONB)
    provider_metadata: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    transfer: Mapped["Transfer"] = relationship("Transfer", back_populates="payment_references")
    payment_method: Mapped["PaymentMethod"] = relationship("PaymentMethod", back_populates="payment_references")
