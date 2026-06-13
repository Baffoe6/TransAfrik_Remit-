from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProviderHealthCheck(Base):
    __tablename__ = "provider_health_checks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class OperationsQueueStatus(Base):
    __tablename__ = "operations_queue_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    queue_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pending_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    last_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    details: Mapped[dict | None] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
