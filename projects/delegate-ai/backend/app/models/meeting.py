from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class MeetingStatus(PyEnum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Meeting details
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String, nullable=False)
    location = Column(String, nullable=True)
    meeting_url = Column(String, nullable=True)  # For virtual meetings

    # Status and metadata
    status = Column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(Text, nullable=True)  # JSON string

    # Calendar integration
    calendar_event_id = Column(String, nullable=True)  # External calendar ID
    calendar_provider = Column(String, nullable=True)  # google, microsoft, etc.

    # Meeting preparation
    agenda = Column(Text, nullable=True)
    preparation_notes = Column(Text, nullable=True)
    ai_briefing = Column(Text, nullable=True)  # AI-generated meeting briefing

    # Attendees and participants
    attendees = Column(Text, nullable=True)  # JSON array of attendee emails

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="meetings")
    tasks = relationship("Task", back_populates="meeting")