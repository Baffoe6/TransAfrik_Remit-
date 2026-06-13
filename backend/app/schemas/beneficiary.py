from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.utils.phone import validate_phone_number


class BeneficiaryCreate(BaseModel):
    beneficiary_type: Literal["mobile_money", "bank_account", "cash_pickup"] = "mobile_money"
    full_name: str = Field(min_length=2, max_length=200)
    account_name: str | None = Field(default=None, max_length=200)
    country: str = Field(default="GH", max_length=2)
    mobile_money_provider: str | None = Field(default=None, max_length=100)
    mobile_wallet_number: str | None = Field(default=None, max_length=30)
    bank_name: str | None = Field(default=None, max_length=100)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_branch: str | None = Field(default=None, max_length=100)
    pickup_location: str | None = Field(default=None, max_length=200)
    pickup_city: str | None = Field(default=None, max_length=100)
    relationship_to_sender: str = Field(min_length=2, max_length=100)

    @model_validator(mode="after")
    def validate_type_fields(self):
        if self.beneficiary_type == "mobile_money":
            if not self.mobile_money_provider or not self.mobile_wallet_number:
                raise ValueError("mobile_money_provider and mobile_wallet_number required for mobile money")
            try:
                self.mobile_wallet_number = validate_phone_number(
                    self.mobile_wallet_number, default_country_code="233"
                )
            except ValueError as exc:
                raise ValueError(f"Invalid beneficiary mobile number: {exc}") from exc
        elif self.beneficiary_type == "bank_account":
            if not self.bank_name or not self.bank_account_number:
                raise ValueError("bank_name and bank_account_number required for bank account")
        elif self.beneficiary_type == "cash_pickup":
            if not self.pickup_location or not self.pickup_city:
                raise ValueError("pickup_location and pickup_city required for cash pickup")
        return self


class BeneficiaryUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    account_name: str | None = Field(default=None, max_length=200)
    mobile_money_provider: str | None = Field(default=None, max_length=100)
    mobile_wallet_number: str | None = Field(default=None, max_length=30)
    bank_name: str | None = Field(default=None, max_length=100)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_branch: str | None = Field(default=None, max_length=100)
    pickup_location: str | None = Field(default=None, max_length=200)
    pickup_city: str | None = Field(default=None, max_length=100)
    relationship_to_sender: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None

    @field_validator("mobile_wallet_number")
    @classmethod
    def normalize_wallet(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validate_phone_number(v, default_country_code="233")


class BeneficiaryResponse(BaseModel):
    id: int
    user_id: int
    beneficiary_type: str
    full_name: str
    account_name: str | None
    country: str
    mobile_money_provider: str | None
    mobile_wallet_number: str | None
    bank_name: str | None
    bank_account_number: str | None
    bank_branch: str | None
    pickup_location: str | None
    pickup_city: str | None
    relationship_to_sender: str
    status: str
    rejection_reason: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
