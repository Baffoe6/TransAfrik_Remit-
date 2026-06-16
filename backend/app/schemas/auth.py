import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.utils.phone import is_email_identifier, validate_phone_number

PIN_PATTERN = re.compile(r"^\d{4,6}$")


def _validate_pin(v: str) -> str:
    v = v.strip()
    if not PIN_PATTERN.match(v):
        raise ValueError("PIN must be 4–6 digits")
    return v


class RegisterRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    pin: str | None = Field(default=None, min_length=4, max_length=6)
    email: EmailStr | None = None
    invite_code: str | None = Field(default=None, max_length=32)
    referral_code: str | None = Field(default=None, max_length=32)
    accept_popia: bool = False
    accept_terms: bool = False
    # Legacy v2.0 APK — password registration until PIN build is installed
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _validate_pin(v)

    @model_validator(mode="after")
    def require_pin_or_password(self):
        if not self.pin and not self.password:
            raise ValueError("4-digit PIN is required")
        if self.pin and (not self.accept_popia or not self.accept_terms):
            raise ValueError("POPIA and Terms consent required")
        return self


class PinLoginRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    pin: str = Field(min_length=4, max_length=6)
    device_id: str | None = Field(default=None, max_length=64)
    device_label: str | None = Field(default=None, max_length=100)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        return _validate_pin(v)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255, description="Mobile number or email")
    password: str
    mfa_code: str | None = None
    device_id: str | None = Field(default=None, max_length=64)
    device_label: str | None = Field(default=None, max_length=100)

    @property
    def is_email_login(self) -> bool:
        return is_email_identifier(self.identifier)


class OtpSendRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    channel: str = Field(description="sms or whatsapp")
    purpose: str = Field(
        description="login, verify_phone, step_up, pin_reset, beneficiary_change, high_value_transfer, kyc_update"
    )

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


class OtpLoginRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    code: str = Field(min_length=4, max_length=8)
    device_id: str | None = Field(default=None, max_length=64)
    device_label: str | None = Field(default=None, max_length=100)
    trust_device: bool = True

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


class OtpVerifyPhoneRequest(BaseModel):
    code: str = Field(min_length=4, max_length=8)
    channel: str = "sms"


class StepUpLoginRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    code: str = Field(min_length=4, max_length=8)
    device_id: str | None = Field(default=None, max_length=64)
    device_label: str | None = Field(default=None, max_length=100)
    trust_device: bool = True

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


class PasswordResetRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


class PinResetConfirm(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    code: str = Field(min_length=4, max_length=8)
    new_pin: str = Field(min_length=4, max_length=6)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)

    @field_validator("new_pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        return _validate_pin(v)


class PasswordResetConfirm(BaseModel):
    """Legacy password reset — prefer PinResetConfirm for customers."""

    mobile_number: str = Field(min_length=8, max_length=30)
    code: str = Field(min_length=4, max_length=8)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


class SetPinRequest(BaseModel):
    """Optional PIN setup for legacy email/password customers."""

    pin: str = Field(min_length=4, max_length=6)
    current_password: str | None = None

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        return _validate_pin(v)


class DeviceTrustRequest(BaseModel):
    device_id: int
    trusted: bool = True


class TokenResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    mfa_required: bool = False
    step_up_required: bool = False
    step_up_mobile: str | None = None
    risk_score: int | None = None
    risk_level: str | None = None
    mfa_setup_required: bool = False
    password_change_required: bool = False
    phone_verification_required: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    mobile_number: str | None
    email: str | None
    first_name: str | None = None
    last_name: str | None = None
    role: str
    status: str = "active"
    email_verified: bool
    phone_verified: bool
    has_pin: bool = False

    model_config = {"from_attributes": True}
