from pydantic import BaseModel, EmailStr, Field





class RegisterRequest(BaseModel):

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)

    phone: str | None = Field(default=None, max_length=20)

    first_name: str = Field(min_length=1, max_length=100)

    last_name: str = Field(min_length=1, max_length=100)

    invite_code: str | None = Field(default=None, max_length=32)





class LoginRequest(BaseModel):

    email: EmailStr

    password: str

    mfa_code: str | None = None





class TokenResponse(BaseModel):

    access_token: str | None = None

    refresh_token: str | None = None

    token_type: str = "bearer"

    mfa_required: bool = False





class RefreshRequest(BaseModel):

    refresh_token: str





class LogoutRequest(BaseModel):

    refresh_token: str





class UserResponse(BaseModel):

    id: int

    email: str

    phone: str | None

    role: str

    email_verified: bool

    phone_verified: bool



    model_config = {"from_attributes": True}

