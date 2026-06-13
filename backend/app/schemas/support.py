from datetime import datetime

from pydantic import BaseModel, Field


class SupportTicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10)
    priority: str = "normal"
    transfer_id: int | None = None


class SupportTicketResponse(BaseModel):
    id: int
    subject: str
    message: str
    status: str
    priority: str = "normal"
    transfer_id: int | None = None
    sla_due_at: datetime | None = None
    escalated: bool = False
    resolution: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
