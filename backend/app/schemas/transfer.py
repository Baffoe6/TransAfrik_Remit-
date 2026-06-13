from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CalculatorRequest(BaseModel):
    send_amount_zar: Decimal = Field(gt=0, decimal_places=2)
    destination_country: str = "GH"
    payment_method_id: int | None = None


class CalculatorResponse(BaseModel):
    send_amount_zar: Decimal
    fee_zar: Decimal
    exchange_rate: Decimal
    receive_amount_ghs: Decimal
    total_amount_zar: Decimal
    from_currency: str = "ZAR"
    to_currency: str = "GHS"


class TransferCreate(BaseModel):
    beneficiary_id: int
    send_amount_zar: Decimal = Field(gt=0, decimal_places=2)
    payment_method_code: str | None = None


class TransferResponse(BaseModel):
    id: int
    reference: str
    user_id: int
    beneficiary_id: int
    payment_method_id: int | None
    status: str
    send_amount_zar: Decimal
    fee_zar: Decimal
    exchange_rate: Decimal
    receive_amount_ghs: Decimal
    total_amount_zar: Decimal
    aml_flags: list | dict | None
    risk_score: int
    compliance_approved: bool
    rejection_reason: str | None
    batch_export_id: str | None
    provider_reference: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class TransferDetailResponse(TransferResponse):
    payment_reference: "PaymentReferenceBrief | None" = None
    timeline: list[dict] = []


class PaymentReferenceBrief(BaseModel):
    reference_number: str
    voucher_number: str | None
    barcode_data: str | None
    qr_data: str | None
    expiry_date: str | None
    status: str
    banking_instructions: dict | None


class TransferStatusUpdate(BaseModel):
    status: str
    notes: str | None = None
    rejection_reason: str | None = None


class TransferStatusHistoryResponse(BaseModel):
    id: int
    from_status: str | None
    to_status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
