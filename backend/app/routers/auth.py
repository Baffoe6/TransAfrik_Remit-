from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.rate_limit import limiter
from app.dependencies import get_client_ip, get_current_user, get_optional_user
from app.models.customer_profile import CustomerProfile
from app.models.enums import SecurityEventType, UserRole
from app.models.security import UserMfa
from app.models.user import User
from app.redis.otp_store import clear_stepup, get_stepup, store_stepup
from app.schemas.auth import (
    DeviceTrustRequest,
    LoginRequest,
    LogoutRequest,
    OtpLoginRequest,
    OtpSendRequest,
    OtpVerifyPhoneRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PinLoginRequest,
    PinResetConfirm,
    RefreshRequest,
    RegisterRequest,
    SetPinRequest,
    StepUpLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.account_security_service import (
    is_account_locked,
    is_staff_user,
    password_is_expired,
    password_was_used_recently,
    record_failed_login,
    record_password_change,
    record_successful_login,
)
from app.services.anomaly_detection_service import analyze_login_risk
from app.services.ip_allowlist_service import is_ip_allowed_for_admin
from app.services.device_trust_service import (
    compute_login_risk,
    fingerprint_device,
    list_user_devices,
    record_device_login,
    set_device_trust,
)
from app.config import get_settings
from app.services.otp_service import (
    OTP_PURPOSE_BENEFICIARY_CHANGE,
    OTP_PURPOSE_HIGH_VALUE_TRANSFER,
    OTP_PURPOSE_KYC_UPDATE,
    OTP_PURPOSE_LOGIN,
    OTP_PURPOSE_PASSWORD_RESET,
    OTP_PURPOSE_PIN_RESET,
    OTP_PURPOSE_STEP_UP,
    OTP_PURPOSE_VERIFY_PHONE,
    find_user_by_mobile,
    send_otp,
    verify_otp_code,
)
from app.services.security_service import (
    create_session,
    log_security_event,
    revoke_session,
    validate_refresh_session,
    verify_mfa_code,
)
from app.services.pilot_service import register_pilot_customer, validate_invite_for_registration
from app.utils.phone import is_email_identifier, validate_phone_number
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_pin,
    verify_password,
    verify_pin,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
optional_bearer = HTTPBearer(auto_error=False)
settings = get_settings()


def _issue_tokens(
    db: Session,
    user: User,
    request: Request,
    *,
    device_id: str | None = None,
    device_label: str | None = None,
    risk_score: int = 0,
    trust_device: bool = False,
    mfa_setup_required: bool = False,
) -> TokenResponse:
    role = user.role.value if isinstance(user.role, UserRole) else user.role
    access = create_access_token(user.id, {"role": role})
    refresh = create_refresh_token(user.id)
    create_session(
        db,
        user_id=user.id,
        refresh_token=refresh,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    fingerprint = fingerprint_device(device_id, request.headers.get("User-Agent"))
    record_device_login(
        db,
        user_id=user.id,
        fingerprint=fingerprint,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        device_label=device_label,
        risk_score=risk_score,
        trust_device=trust_device,
    )
    log_security_event(
        db,
        event_type=SecurityEventType.LOGIN_SUCCESS,
        user_id=user.id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=f"risk_score={risk_score}",
    )
    record_successful_login(db, user)
    db.commit()
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        mfa_setup_required=mfa_setup_required,
        password_change_required=password_is_expired(user),
    )


def _staff_mfa_state(db: Session, user: User) -> dict:
    if not is_staff_user(user):
        return {"enabled": False, "setup_required": False, "verify_required": False}
    mfa = db.query(UserMfa).filter(UserMfa.user_id == user.id, UserMfa.is_enabled.is_(True)).first()
    enabled = mfa is not None
    setup_required = settings.admin_mfa_required and not enabled
    return {"enabled": enabled, "setup_required": setup_required, "verify_required": enabled}


def _find_user_by_identifier(db: Session, identifier: str) -> User | None:
    if is_email_identifier(identifier):
        return db.query(User).filter(User.email == identifier.strip().lower()).first()
    try:
        mobile = validate_phone_number(identifier)
    except ValueError:
        return None
    return db.query(User).filter(User.mobile_number == mobile).first()


def _user_response(user: User) -> UserResponse:
    role = user.role.value if isinstance(user.role, UserRole) else user.role
    return UserResponse(
        id=user.id,
        mobile_number=user.mobile_number,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=role,
        status=user.status,
        email_verified=user.email_verified,
        phone_verified=user.phone_verified,
        has_pin=bool(user.pin_hash),
    )


def _post_credential_login(
    request: Request,
    db: Session,
    user: User,
    *,
    device_id: str | None,
    device_label: str | None,
    mfa_code: str | None = None,
) -> TokenResponse:
    """Shared flow after PIN/password verified: MFA, risk, step-up, tokens."""
    ip = get_client_ip(request)

    if is_account_locked(user):
        db.commit()
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Account temporarily locked due to failed login attempts")

    if not user.is_active or user.status == "inactive":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    if not is_ip_allowed_for_admin(db, user, ip):
        log_security_event(
            db,
            event_type=SecurityEventType.IP_BLOCKED,
            user_id=user.id,
            ip_address=ip,
            details="Admin login blocked by IP allowlist",
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Login not permitted from this IP address")

    mfa_state = _staff_mfa_state(db, user)
    if mfa_state["setup_required"]:
        db.commit()
        return _issue_tokens(
            db, user, request,
            device_id=device_id,
            device_label=device_label,
            mfa_setup_required=True,
        )

    if mfa_state["verify_required"]:
        if not mfa_code:
            db.commit()
            return TokenResponse(mfa_required=True)
        if not verify_mfa_code(db, user.id, mfa_code):
            log_security_event(db, event_type=SecurityEventType.MFA_FAILED, user_id=user.id, ip_address=ip)
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
        log_security_event(db, event_type=SecurityEventType.MFA_VERIFIED, user_id=user.id, ip_address=ip)

    fingerprint = fingerprint_device(device_id, request.headers.get("User-Agent"))
    risk = compute_login_risk(
        db,
        user_id=user.id,
        fingerprint=fingerprint,
        ip_address=ip,
        user_agent=request.headers.get("User-Agent"),
    )
    analyze_login_risk(
        db,
        user=user,
        ip_address=ip,
        risk_score=risk["risk_score"],
        risk_factors=risk["factors"],
    )

    if risk["requires_step_up"] and user.mobile_number:
        store_stepup(user.mobile_number, user.id, risk["risk_score"])
        send_otp(
            mobile=user.mobile_number,
            channel="sms",
            purpose=OTP_PURPOSE_STEP_UP,
            user_id=user.id,
        )
        log_security_event(
            db,
            event_type=SecurityEventType.STEP_UP_REQUIRED,
            user_id=user.id,
            ip_address=ip,
            details=f"risk_score={risk['risk_score']} factors={risk['factors']}",
        )
        db.commit()
        return TokenResponse(
            step_up_required=True,
            step_up_mobile=user.mobile_number,
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
        )

    if password_is_expired(user):
        log_security_event(
            db,
            event_type=SecurityEventType.PASSWORD_EXPIRED,
            user_id=user.id,
            ip_address=ip,
        )

    return _issue_tokens(
        db,
        user,
        request,
        device_id=device_id,
        device_label=device_label,
        risk_score=risk["risk_score"],
        trust_device=risk["device_trusted"],
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, data: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    mobile = data.mobile_number
    email = str(data.email).lower() if data.email else None

    if db.query(User).filter(User.mobile_number == mobile).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number already registered")

    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        mobile_number=mobile,
        email=email,
        first_name=data.first_name,
        last_name=data.last_name,
        pin_hash=hash_pin(data.pin),
        password_hash=hash_password(data.password) if data.password else None,
        role=UserRole.CUSTOMER,
        status="active",
    )
    db.add(user)
    db.flush()

    profile = CustomerProfile(
        user_id=user.id,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(profile)
    db.flush()

    invite = validate_invite_for_registration(db, email, mobile, data.invite_code)
    register_pilot_customer(db, user.id, invite)

    if data.referral_code:
        from app.services.referral_program_service import record_referral_signup

        record_referral_signup(db, data.referral_code.strip().upper(), user.id)

    return _issue_tokens(db, user, request)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, data: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    """Legacy email + password login for staff and migrated accounts."""
    ip = get_client_ip(request)
    user = _find_user_by_identifier(db, data.identifier)
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        record_failed_login(db, user, ip, data.identifier)
        log_security_event(
            db,
            event_type=SecurityEventType.LOGIN_FAILED,
            user_id=user.id if user else None,
            ip_address=ip,
            details=f"Failed login attempt for {data.identifier}",
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return _post_credential_login(
        request,
        db,
        user,
        device_id=data.device_id,
        device_label=data.device_label,
        mfa_code=data.mfa_code,
    )


@router.post("/login/pin", response_model=TokenResponse)
@limiter.limit("10/minute")
def login_with_pin(request: Request, data: PinLoginRequest, db: Annotated[Session, Depends(get_db)]):
    """Primary customer login — mobile number + 4-digit PIN."""
    ip = get_client_ip(request)
    user = find_user_by_mobile(db, data.mobile_number)
    if not user or not user.pin_hash or not verify_pin(data.pin, user.pin_hash):
        record_failed_login(db, user, ip, data.mobile_number)
        log_security_event(
            db,
            event_type=SecurityEventType.LOGIN_FAILED,
            user_id=user.id if user else None,
            ip_address=ip,
            details=f"Failed PIN login for {data.mobile_number}",
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid mobile number or PIN")

    return _post_credential_login(
        request,
        db,
        user,
        device_id=data.device_id,
        device_label=data.device_label,
    )


@router.post("/otp/send")
@limiter.limit("5/minute")
def otp_send(
    request: Request,
    data: OtpSendRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_user)],
):
    if data.purpose == OTP_PURPOSE_VERIFY_PHONE:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if data.mobile_number != current_user.mobile_number:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number mismatch")
        user_id = current_user.id
    elif data.purpose == OTP_PURPOSE_LOGIN:
        user = find_user_by_mobile(db, data.mobile_number)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this mobile number")
        user_id = user.id
    elif data.purpose in (OTP_PURPOSE_PASSWORD_RESET, OTP_PURPOSE_PIN_RESET):
        user = find_user_by_mobile(db, data.mobile_number)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this mobile number")
        user_id = user.id
    elif data.purpose in (
        OTP_PURPOSE_BENEFICIARY_CHANGE,
        OTP_PURPOSE_HIGH_VALUE_TRANSFER,
        OTP_PURPOSE_KYC_UPDATE,
    ):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if data.mobile_number != current_user.mobile_number:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number mismatch")
        user_id = current_user.id
    elif data.purpose == OTP_PURPOSE_STEP_UP:
        stepup = get_stepup(data.mobile_number)
        if not stepup:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending step-up verification")
        user_id = stepup["user_id"]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purpose")

    result = send_otp(
        mobile=data.mobile_number,
        channel=data.channel,
        purpose=data.purpose,
        user_id=user_id,
    )
    log_security_event(
        db,
        event_type=SecurityEventType.OTP_SENT,
        user_id=user_id,
        ip_address=get_client_ip(request),
        details=f"channel={data.channel} purpose={data.purpose}",
    )
    db.commit()
    return result


@router.post("/login/otp", response_model=TokenResponse)
@limiter.limit("10/minute")
def login_with_otp(request: Request, data: OtpLoginRequest, db: Annotated[Session, Depends(get_db)]):
    """Passwordless login via SMS or WhatsApp OTP."""
    user = find_user_by_mobile(db, data.mobile_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this mobile number")
    if not user.is_active or user.status == "inactive":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    try:
        verify_otp_code(data.mobile_number, OTP_PURPOSE_LOGIN, data.code)
    except HTTPException:
        log_security_event(
            db,
            event_type=SecurityEventType.OTP_FAILED,
            user_id=user.id,
            ip_address=get_client_ip(request),
            details="passwordless_login",
        )
        db.commit()
        raise

    fingerprint = fingerprint_device(data.device_id, request.headers.get("User-Agent"))
    risk = compute_login_risk(
        db,
        user_id=user.id,
        fingerprint=fingerprint,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    log_security_event(
        db,
        event_type=SecurityEventType.OTP_VERIFIED,
        user_id=user.id,
        ip_address=get_client_ip(request),
        details="passwordless_login",
    )
    return _issue_tokens(
        db,
        user,
        request,
        device_id=data.device_id,
        device_label=data.device_label,
        risk_score=risk["risk_score"],
        trust_device=data.trust_device,
    )


@router.post("/login/step-up", response_model=TokenResponse)
@limiter.limit("10/minute")
def login_step_up(request: Request, data: StepUpLoginRequest, db: Annotated[Session, Depends(get_db)]):
    """Complete password login after OTP step-up for high-risk / new devices."""
    stepup = get_stepup(data.mobile_number)
    if not stepup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending step-up verification")

    user = db.query(User).filter(User.id == stepup["user_id"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        verify_otp_code(data.mobile_number, OTP_PURPOSE_STEP_UP, data.code)
    except HTTPException:
        log_security_event(
            db,
            event_type=SecurityEventType.OTP_FAILED,
            user_id=user.id,
            ip_address=get_client_ip(request),
            details="step_up_login",
        )
        db.commit()
        raise

    clear_stepup(data.mobile_number)
    log_security_event(
        db,
        event_type=SecurityEventType.OTP_VERIFIED,
        user_id=user.id,
        ip_address=get_client_ip(request),
        details="step_up_login",
    )
    return _issue_tokens(
        db,
        user,
        request,
        device_id=data.device_id,
        device_label=data.device_label,
        risk_score=stepup["risk_score"],
        trust_device=data.trust_device,
    )


@router.post("/otp/verify-phone")
@limiter.limit("10/minute")
def verify_phone_with_otp(
    request: Request,
    data: OtpVerifyPhoneRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Verify mobile number via SMS or WhatsApp OTP."""
    if not current_user.mobile_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No mobile number on account")

    try:
        verify_otp_code(current_user.mobile_number, OTP_PURPOSE_VERIFY_PHONE, data.code)
    except HTTPException:
        log_security_event(
            db,
            event_type=SecurityEventType.OTP_FAILED,
            user_id=current_user.id,
            ip_address=get_client_ip(request),
            details="verify_phone",
        )
        db.commit()
        raise

    current_user.phone_verified = True
    log_security_event(
        db,
        event_type=SecurityEventType.OTP_VERIFIED,
        user_id=current_user.id,
        ip_address=get_client_ip(request),
        details="verify_phone",
    )
    db.commit()
    return {
        "verified": True,
        "mobile_number": current_user.mobile_number,
        "message": "Mobile number verified successfully",
    }


@router.get("/devices")
def list_devices(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    devices = list_user_devices(db, current_user.id)
    return {
        "devices": [
            {
                "id": d.id,
                "device_label": d.device_label,
                "is_trusted": d.is_trusted,
                "risk_score": d.risk_score,
                "login_count": d.login_count,
                "last_seen_at": d.last_seen_at.isoformat() if d.last_seen_at else None,
                "trusted_at": d.trusted_at.isoformat() if d.trusted_at else None,
            }
            for d in devices
        ]
    }


@router.post("/devices/trust")
def trust_device(
    data: DeviceTrustRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    device = set_device_trust(db, current_user.id, data.device_id, data.trusted)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    log_security_event(
        db,
        event_type=SecurityEventType.DEVICE_TRUSTED,
        user_id=current_user.id,
        ip_address=get_client_ip(request),
        details=f"device_id={data.device_id} trusted={data.trusted}",
    )
    db.commit()
    return {"device_id": device.id, "is_trusted": device.is_trusted}


@router.post("/password/forgot")
@limiter.limit("5/minute")
def password_forgot(request: Request, data: PasswordResetRequest, db: Annotated[Session, Depends(get_db)]):
    user = find_user_by_mobile(db, data.mobile_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this mobile number")
    purpose = OTP_PURPOSE_PIN_RESET if user.pin_hash else OTP_PURPOSE_PASSWORD_RESET
    result = send_otp(mobile=data.mobile_number, channel="sms", purpose=purpose, user_id=user.id)
    log_security_event(db, event_type=SecurityEventType.OTP_SENT, user_id=user.id, ip_address=get_client_ip(request), details=purpose)
    db.commit()
    return result


@router.post("/pin/forgot")
@limiter.limit("5/minute")
def pin_forgot(request: Request, data: PasswordResetRequest, db: Annotated[Session, Depends(get_db)]):
    """Request OTP to reset 4-digit PIN."""
    return password_forgot(request, data, db)


@router.post("/password/reset")
@limiter.limit("5/minute")
def password_reset(request: Request, data: PasswordResetConfirm, db: Annotated[Session, Depends(get_db)]):
    user = find_user_by_mobile(db, data.mobile_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this mobile number")
    try:
        verify_otp_code(data.mobile_number, OTP_PURPOSE_PASSWORD_RESET, data.code)
    except HTTPException:
        log_security_event(db, event_type=SecurityEventType.OTP_FAILED, user_id=user.id, ip_address=get_client_ip(request), details="password_reset")
        db.commit()
        raise
    if password_was_used_recently(db, user, data.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password was used recently; choose a different password")
    record_password_change(db, user, hash_password(data.new_password))
    log_security_event(db, event_type=SecurityEventType.PASSWORD_CHANGED, user_id=user.id, ip_address=get_client_ip(request), details="password_reset_otp")
    db.commit()
    return {"message": "Password reset successfully"}


@router.post("/pin/reset")
@limiter.limit("5/minute")
def pin_reset(request: Request, data: PinResetConfirm, db: Annotated[Session, Depends(get_db)]):
    user = find_user_by_mobile(db, data.mobile_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this mobile number")
    try:
        verify_otp_code(data.mobile_number, OTP_PURPOSE_PIN_RESET, data.code)
    except HTTPException:
        log_security_event(db, event_type=SecurityEventType.OTP_FAILED, user_id=user.id, ip_address=get_client_ip(request), details="pin_reset")
        db.commit()
        raise
    if user.pin_hash and verify_pin(data.new_pin, user.pin_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New PIN must be different from your current PIN")
    user.pin_hash = hash_pin(data.new_pin)
    record_successful_login(db, user)
    log_security_event(db, event_type=SecurityEventType.PASSWORD_CHANGED, user_id=user.id, ip_address=get_client_ip(request), details="pin_reset_otp")
    db.commit()
    return {"message": "PIN reset successfully"}


@router.post("/pin/set")
def set_pin(
    data: SetPinRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    """Allow legacy email/password customers to create a PIN for mobile login."""
    if current_user.pin_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PIN already set")
    if current_user.password_hash:
        if not data.current_password or not verify_password(data.current_password, current_user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password required")
    current_user.pin_hash = hash_pin(data.pin)
    log_security_event(
        db,
        event_type=SecurityEventType.PASSWORD_CHANGED,
        user_id=current_user.id,
        ip_address=get_client_ip(request),
        details="pin_set",
    )
    db.commit()
    return {"message": "PIN created successfully", "has_pin": True}


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh_token(request: Request, data: RefreshRequest, db: Annotated[Session, Depends(get_db)]):
    session = validate_refresh_session(db, data.refresh_token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    log_security_event(
        db,
        event_type=SecurityEventType.TOKEN_REFRESH,
        user_id=user.id,
        ip_address=get_client_ip(request),
    )
    revoke_session(db, data.refresh_token)
    return _issue_tokens(db, user, request)


@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    auth: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer)] = None,
):
    if auth and auth.credentials:
        access_payload = decode_token(auth.credentials)
        if access_payload and access_payload.get("jti"):
            from app.redis.session_blacklist import blacklist_token

            blacklist_token(access_payload["jti"])

    revoke_session(db, data.refresh_token)
    payload = decode_token(data.refresh_token)
    user_id = int(payload["sub"]) if payload and payload.get("sub") else None
    log_security_event(
        db,
        event_type=SecurityEventType.LOGOUT,
        user_id=user_id,
        ip_address=get_client_ip(request),
    )
    db.commit()
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return _user_response(current_user)


@router.post("/verify-email")
def verify_email_placeholder(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    if not current_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No email on account")
    current_user.email_verified = True
    db.commit()
    return {"message": "Email verification placeholder — marked as verified"}
