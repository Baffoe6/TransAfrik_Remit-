from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AgentCommissionStatus, ReferralType


class AgentProfile(Base):
    __tablename__ = "agent_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    agent_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100))
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.50"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    referrals: Mapped[list["AgentReferral"]] = relationship("AgentReferral", back_populates="agent")
    commissions: Mapped[list["AgentCommission"]] = relationship("AgentCommission", back_populates="agent")


class AgentReferral(Base):
    __tablename__ = "agent_referrals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_profiles.id", ondelete="CASCADE"), index=True)
    customer_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id", ondelete="SET NULL"), index=True)
    referral_type: Mapped[ReferralType] = mapped_column(String(20), nullable=False, index=True)
    referral_code_used: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    agent: Mapped["AgentProfile"] = relationship("AgentProfile", back_populates="referrals")


class AgentCommission(Base):
    __tablename__ = "agent_commissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_profiles.id", ondelete="CASCADE"), index=True)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id", ondelete="CASCADE"), index=True)
    transfer_amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    commission_amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[AgentCommissionStatus] = mapped_column(String(20), default=AgentCommissionStatus.PENDING, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    agent: Mapped["AgentProfile"] = relationship("AgentProfile", back_populates="commissions")
