from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WhatsAppConversationLog(Base):
    __tablename__ = "whatsapp_conversation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_code: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), default="inbound")
    menu_option: Mapped[str | None] = mapped_column(String(50))
    message_body: Mapped[str | None] = mapped_column(Text)
    response_body: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id", ondelete="SET NULL"))
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
