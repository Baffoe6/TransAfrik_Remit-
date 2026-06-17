from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import InAppReadStatus, NotificationDeliveryChannel, NotificationDeliveryStatus


class UserNotification(Base):
    """Customer in-app notification inbox."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id", ondelete="SET NULL"), index=True)
    notification_type: Mapped[str] = mapped_column(String(30), default="transfer_status")
    event_code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    transfer_reference: Mapped[str | None] = mapped_column(String(20))
    read_status: Mapped[str] = mapped_column(String(10), default=InAppReadStatus.UNREAD.value, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    deliveries: Mapped[list["NotificationDelivery"]] = relationship(
        "NotificationDelivery", back_populates="notification", cascade="all, delete-orphan"
    )


class NotificationDelivery(Base):
    """Per-channel delivery attempt for a notification."""

    __tablename__ = "notification_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=NotificationDeliveryStatus.PENDING.value, index=True)
    recipient: Mapped[str | None] = mapped_column(String(255))
    provider_response: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    notification: Mapped["UserNotification"] = relationship("UserNotification", back_populates="deliveries")
