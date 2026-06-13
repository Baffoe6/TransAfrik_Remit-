from datetime import datetime

from pydantic import BaseModel


class KycDocumentResponse(BaseModel):
    id: int
    document_type: str
    original_filename: str
    status: str
    rejection_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
