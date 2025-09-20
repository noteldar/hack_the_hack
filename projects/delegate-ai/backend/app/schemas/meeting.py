from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.meeting import MeetingStatus


# Shared properties
class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    timezone: str
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None
    agenda: Optional[str] = None
    attendees: Optional[List[str]] = None


# Properties to receive on creation
class MeetingCreate(MeetingBase):
    calendar_event_id: Optional[str] = None
    calendar_provider: Optional[str] = None


# Properties to receive on update
class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    status: Optional[MeetingStatus] = None
    agenda: Optional[str] = None
    preparation_notes: Optional[str] = None
    ai_briefing: Optional[str] = None
    attendees: Optional[List[str]] = None


# Properties stored in database
class MeetingInDB(MeetingBase):
    id: int
    status: MeetingStatus
    calendar_event_id: Optional[str] = None
    calendar_provider: Optional[str] = None
    preparation_notes: Optional[str] = None
    ai_briefing: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class Meeting(MeetingInDB):
    pass