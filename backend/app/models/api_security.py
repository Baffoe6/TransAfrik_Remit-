from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import ApiEnvironment, ApiKeyStatus


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    environment: Mapped[ApiEnvironment] = mapped_column(String(20), default=ApiEnvironment.DEVELOPMENT)
    status: Mapped[ApiKeyStatus] = mapped_column(String(20), default=ApiKeyStatus.ACTIVE)
    scopes: Mapped[list | None] = mapped_column(JSONB)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProviderSecret(Base):
    __tablename__ = "provider_secrets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    secret_name: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    environment: Mapped[ApiEnvironment] = mapped_column(String(20), default=ApiEnvironment.DEVELOPMENT)
    credential_type: Mapped[str] = mapped_column(String(50), default="api_key")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validation_status: Mapped[str | None] = mapped_column(String(30))
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SecurityMonitorEvent(Base):
    __tablename__ = "security_monitor_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_ip: Mapped[str | None] = mapped_column(String(45))
    path: Mapped[str | None] = mapped_column(String(255))
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
