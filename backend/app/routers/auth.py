from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.rate_limit import limiter
from app.dependencies import get_client_ip, get_current_user
from app.models.customer_profile import CustomerProfile
from app.models.enums import SecurityEventType, UserRole
from app.models.security import UserMfa
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.security_service import (
    create_session,
    log_security_event,
    revoke_session,
    validate_refresh_session,
    verify_mfa_code,
)
from app.services.pilot_service import register_pilot_customer, validate_invite_for_registration
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
optional_bearer = HTTPBearer(auto_error=False)


def _issue_tokens(db: Session, user: User, request: Request) -> TokenResponse:
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
    log_security_event(
        db,
        event_type=SecurityEventType.LOGIN_SUCCESS,
        user_id=user.id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


def _staff_requires_mfa(db: Session, user: User) -> bool:
    if user.role == UserRole.CUSTOMER:
        return False
    mfa = db.query(UserMfa).filter(UserMfa.user_id == user.id, UserMfa.is_enabled.is_(True)).first()
    return mfa is not None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, data: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if data.phone and db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")

    user = User(
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.CUSTOMER,
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

    invite = validate_invite_for_registration(db, data.email, data.invite_code)
    register_pilot_customer(db, user.id, invite)

    return _issue_tokens(db, user, request)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, data: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        log_security_event(
            db,
            event_type=SecurityEventType.LOGIN_FAILED,
            ip_address=get_client_ip(request),
            details=f"Failed login attempt for {data.email}",
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    if _staff_requires_mfa(db, user):
        if not data.mfa_code:
            db.commit()
            return TokenResponse(mfa_required=True)
        if not verify_mfa_code(db, user.id, data.mfa_code):
            log_security_event(
                db,
                event_type=SecurityEventType.MFA_FAILED,
                user_id=user.id,
                ip_address=get_client_ip(request),
            )
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")

    return _issue_tokens(db, user, request)


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
    return current_user


@router.post("/verify-email")
def verify_email_placeholder(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    """Placeholder for email verification — marks as verified in dev."""
    current_user.email_verified = True
    db.commit()
    return {"message": "Email verification placeholder — marked as verified"}


@router.post("/verify-phone")
def verify_phone_placeholder(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    """Placeholder for phone/SMS verification — marks as verified in dev."""
    current_user.phone_verified = True
    db.commit()
    return {"message": "Phone verification placeholder — marked as verified"}
