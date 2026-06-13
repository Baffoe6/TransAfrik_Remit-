from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import PilotCustomerStatus, PilotInviteStatus


class PilotSettings(Base):
    __tablename__ = "pilot_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_mode_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    invite_only_registration: Mapped[bool] = mapped_column(Boolean, default=True)
    require_admin_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    default_max_transfer_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("5000"))
    default_daily_transfer_limit: Mapped[int] = mapped_column(Integer, default=3)
    default_monthly_volume_zar: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("15000"))
    default_allowed_corridors: Mapped[list | None] = mapped_column(JSONB)
    demo_mode_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PilotInvite(Base):
    __tablename__ = "pilot_invites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invite_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[PilotInviteStatus] = mapped_column(String(20), default=PilotInviteStatus.ACTIVE)
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    uses_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PilotCustomer(Base):
    __tablename__ = "pilot_customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    status: Mapped[PilotCustomerStatus] = mapped_column(String(20), default=PilotCustomerStatus.PENDING)
    invite_code_used: Mapped[str | None] = mapped_column(String(32))
    max_transfer_zar: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    daily_transfer_limit: Mapped[int | None] = mapped_column(Integer)
    monthly_volume_zar: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    allowed_corridors: Mapped[list | None] = mapped_column(JSONB)
    admin_notes: Mapped[str | None] = mapped_column(Text)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
