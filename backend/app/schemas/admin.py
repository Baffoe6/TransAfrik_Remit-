from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    total_customers: int
    pending_kyc: int
    pending_transfers: int
    completed_transfers: int
    monthly_volume_zar: Decimal


class KycReviewRequest(BaseModel):
    status: str
    rejection_reason: str | None = None


class BeneficiaryReviewRequest(BaseModel):
    status: str
    rejection_reason: str | None = None


class PaymentVerifyRequest(BaseModel):
    status: str
    rejection_reason: str | None = None


class ExchangeRateCreate(BaseModel):
    from_currency: str = "ZAR"
    to_currency: str = "GHS"
    rate: Decimal = Field(gt=0, decimal_places=6)


class FeeRuleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    min_amount_zar: Decimal = Field(ge=0, decimal_places=2)
    max_amount_zar: Decimal | None = Field(default=None, decimal_places=2)
    fee_type: str = "flat"
    fee_value: Decimal = Field(gt=0, decimal_places=2)


class BatchExportRequest(BaseModel):
    transfer_ids: list[int] = Field(min_length=1)


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    details: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerListItem(BaseModel):
    id: int
    email: str
    phone: str | None
    first_name: str | None
    last_name: str | None
    kyc_status: str | None
    created_at: datetime
    transfer_count: int = 0
