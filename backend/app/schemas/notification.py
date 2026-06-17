from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    event_code: str
    title: str
    message: str
    transfer_id: int | None
    transfer_reference: str | None
    read_status: str
    created_at: datetime
    read_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int


class NotificationDeliveryResponse(BaseModel):
    id: int
    channel: str
    status: str
    recipient: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransferNotificationFeedItem(BaseModel):
    notification: NotificationResponse
    deliveries: list[NotificationDeliveryResponse]


class PushTokenUpdate(BaseModel):
    push_token: str
    push_notifications_enabled: bool = True
