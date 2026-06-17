from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.enums import InAppReadStatus
from app.models.user import User
from app.models.user_notification import UserNotification
from app.schemas.notification import NotificationListResponse, NotificationResponse, PushTokenUpdate
from app.services.transfer_notification_service import mark_all_notifications_read, mark_notification_read

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
):
    items = (
        db.query(UserNotification)
        .filter(UserNotification.user_id == current_user.id)
        .order_by(UserNotification.created_at.desc())
        .limit(min(limit, 100))
        .all()
    )
    unread = (
        db.query(UserNotification)
        .filter(
            UserNotification.user_id == current_user.id,
            UserNotification.read_status == InAppReadStatus.UNREAD.value,
        )
        .count()
    )
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        unread_count=unread,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    notification = (
        db.query(UserNotification)
        .filter(UserNotification.id == notification_id, UserNotification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    mark_notification_read(db, notification)
    db.commit()
    db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.post("/read-all")
def mark_all_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    count = mark_all_notifications_read(db, current_user.id)
    db.commit()
    return {"marked_read": count}


@router.post("/push-token")
def register_push_token(
    data: PushTokenUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    current_user.push_token = data.push_token.strip() or None
    current_user.push_notifications_enabled = data.push_notifications_enabled
    db.commit()
    return {"registered": bool(current_user.push_token), "push_notifications_enabled": current_user.push_notifications_enabled}
