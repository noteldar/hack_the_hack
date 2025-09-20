from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class NotificationType(PyEnum):
    TASK_CREATED = "task_created"
    TASK_DUE = "task_due"
    MEETING_REMINDER = "meeting_reminder"
    EMAIL_PROCESSED = "email_processed"
    AGENT_ACTIVITY = "agent_activity"
    CALENDAR_UPDATE = "calendar_update"
    SYSTEM_ALERT = "system_alert"


class NotificationPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    # Notification metadata
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)

    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)

    # Delivery channels
    send_email = Column(Boolean, default=False)
    send_push = Column(Boolean, default=True)
    send_websocket = Column(Boolean, default=True)

    # Related entities
    related_task_id = Column(Integer, nullable=True)
    related_meeting_id = Column(Integer, nullable=True)
    related_email_id = Column(Integer, nullable=True)
    related_agent_id = Column(Integer, nullable=True)

    # Additional data
    data = Column(Text, nullable=True)  # JSON data for the notification

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")