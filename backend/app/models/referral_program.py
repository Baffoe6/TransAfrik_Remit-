from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import ReferralRewardType, VoucherStatus


class ReferralProgram(Base):
    __tablename__ = "referral_programs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    points_per_referral: Mapped[int] = mapped_column(Integer, default=100)
    points_per_completed_transfer: Mapped[int] = mapped_column(Integer, default=50)
    voucher_threshold_points: Mapped[int] = mapped_column(Integer, default=500)
    voucher_discount_zar: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("25.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CustomerReferral(Base):
    __tablename__ = "customer_referrals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("referral_programs.id", ondelete="CASCADE"))
    referrer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    referred_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    referral_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    converted: Mapped[bool] = mapped_column(default=False)
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReferralReward(Base):
    __tablename__ = "referral_rewards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reward_type: Mapped[ReferralRewardType] = mapped_column(String(30), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)
    referral_id: Mapped[int | None] = mapped_column(ForeignKey("customer_referrals.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DiscountVoucher(Base):
    __tablename__ = "discount_vouchers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    discount_zar: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[VoucherStatus] = mapped_column(String(20), default=VoucherStatus.ACTIVE)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
