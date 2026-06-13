from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import BeneficiaryStatus, BeneficiaryType


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    beneficiary_type: Mapped[BeneficiaryType] = mapped_column(String(30), default=BeneficiaryType.MOBILE_MONEY)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_name: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(2), default="GH", nullable=False)
    mobile_money_provider: Mapped[str | None] = mapped_column(String(100))
    mobile_wallet_number: Mapped[str | None] = mapped_column(String(30))
    bank_name: Mapped[str | None] = mapped_column(String(100))
    bank_account_number: Mapped[str | None] = mapped_column(String(50))
    bank_branch: Mapped[str | None] = mapped_column(String(100))
    pickup_location: Mapped[str | None] = mapped_column(String(200))
    pickup_city: Mapped[str | None] = mapped_column(String(100))
    relationship_to_sender: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[BeneficiaryStatus] = mapped_column(String(20), default=BeneficiaryStatus.PENDING)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="beneficiaries", foreign_keys=[user_id])
    transfers: Mapped[list["Transfer"]] = relationship("Transfer", back_populates="beneficiary")
