from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.phone import is_email_identifier, validate_phone_number


class RegisterRequest(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    invite_code: str | None = Field(default=None, max_length=32)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


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
    purpose: str = Field(description="login, verify_phone, or step_up")

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


class PasswordResetConfirm(BaseModel):
    mobile_number: str = Field(min_length=8, max_length=30)
    code: str = Field(min_length=4, max_length=8)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile(cls, v: str) -> str:
        return validate_phone_number(v)


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

    model_config = {"from_attributes": True}
