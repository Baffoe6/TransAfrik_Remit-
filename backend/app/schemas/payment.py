from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentMethodResponse(BaseModel):
    id: int
    name: str
    code: str
    provider: str
    description: str | None
    requires_proof_upload: bool
    is_instant: bool
    is_active: bool

    model_config = {"from_attributes": True}


class PaymentReferenceResponse(BaseModel):
    id: int
    transfer_id: int
    provider: str
    reference_number: str
    voucher_number: str | None
    barcode_data: str | None
    qr_data: str | None
    amount: Decimal
    currency: str
    expiry_date: date | None
    status: str
    banking_instructions: dict | None
    provider_metadata: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GeneratePaymentRequest(BaseModel):
    payment_method_code: str = Field(min_length=2, max_length=50)


class FlutterwaveSessionResponse(BaseModel):
    payment_url: str
    session_ref: str
    provider: str = "flutterwave"
    status: str = "pending"
    expires_at: str | None = None


class PaymentStatusResponse(BaseModel):
    transfer_id: int
    status: str
    payment_status: str
    reference_number: str | None = None


class PaymentVerificationRequest(BaseModel):
    status: str
    notes: str | None = None
    rejection_reason: str | None = None


class PaymentDashboardStats(BaseModel):
    pending_payments: int
    pending_verifications: int
    expired_references: int
    paid_today: int
    daily_volume_zar: Decimal
    monthly_volume_zar: Decimal


class ComplianceQueueItem(BaseModel):
    transfer_id: int
    reference: str
    customer_email: str
    customer_name: str
    send_amount_zar: Decimal
    risk_score: int
    aml_flags: list | dict | None
    status: str
    created_at: datetime
