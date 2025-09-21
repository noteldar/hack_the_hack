"""
Meeting schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.meeting import MeetingStatus, MeetingPriority


class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendees: Optional[List[str]] = []
    required_attendees: Optional[List[str]] = []
    optional_attendees: Optional[List[str]] = []
    priority: Optional[MeetingPriority] = MeetingPriority.MEDIUM
    meeting_type: Optional[str] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[List[str]] = None
    status: Optional[MeetingStatus] = None
    priority: Optional[MeetingPriority] = None


class MeetingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    location: Optional[str]
    meeting_link: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_minutes: Optional[int]
    status: str
    priority: str
    attendees: Optional[List[str]]
    ai_importance_score: Optional[float]
    ai_decision: Optional[str]
    ai_decision_confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingAnalysisResponse(BaseModel):
    meeting_id: int
    importance_score: Optional[float]
    conflict_score: Optional[float]
    productivity_impact: Optional[float]
    ai_decision: Optional[str]
    decision_confidence: Optional[float]
    reasoning: Optional[str]
    last_analyzed: Optional[datetime]


class MeetingListResponse(BaseModel):
    meetings: List[MeetingResponse]
    total: int
    skip: int
    limit: int