from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.notification import NotificationType, NotificationPriority


# Shared properties
class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    send_email: bool = False
    send_push: bool = True
    send_websocket: bool = True
    data: Optional[Dict[str, Any]] = None


# Properties to receive on creation
class NotificationCreate(NotificationBase):
    related_task_id: Optional[int] = None
    related_meeting_id: Optional[int] = None
    related_email_id: Optional[int] = None
    related_agent_id: Optional[int] = None


# Properties to receive on update
class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_sent: Optional[bool] = None
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


# Properties stored in database
class NotificationInDB(NotificationBase):
    id: int
    is_read: bool
    is_sent: bool
    related_task_id: Optional[int] = None
    related_meeting_id: Optional[int] = None
    related_email_id: Optional[int] = None
    related_agent_id: Optional[int] = None
    user_id: int
    created_at: datetime
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class Notification(NotificationInDB):
    pass