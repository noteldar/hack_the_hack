"""
Advanced Calendar integration schemas with autonomous features
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Add any additional enums if needed
class CalendarPermission(str, Enum):
    READ_CALENDAR = "read_calendar"
    WRITE_CALENDAR = "write_calendar"
    READ_EVENTS = "read_events"
    WRITE_EVENTS = "write_events"
    FREE_BUSY = "free_busy"


class SyncStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"


class CalendarEventCreate(BaseModel):
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, description="Event location")
    start_time: str = Field(..., description="Start time (ISO format)")
    end_time: str = Field(..., description="End time (ISO format)")
    timezone: Optional[str] = Field("UTC", description="Timezone")
    attendees: Optional[List[str]] = Field([], description="Attendee emails")


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    timezone: Optional[str] = None
    attendees: Optional[List[str]] = None


class CalendarEventResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = []
    organizer_email: Optional[str] = None
    meeting_link: Optional[str] = None


class CalendarConnectionResponse(BaseModel):
    status: str
    message: str
    auth_url: Optional[str] = None
    connected_at: Optional[str] = None


class CalendarStatusResponse(BaseModel):
    connected: bool
    message: Optional[str] = None
    connected_at: Optional[str] = None
    calendars: Optional[List[Dict[str, Any]]] = []
    permissions: Optional[Dict[str, bool]] = {}
    primary_calendar: Optional[Dict[str, Any]] = None
    recent_events_count: Optional[int] = 0


class CalendarSyncRequest(BaseModel):
    days_back: Optional[int] = Field(7, description="Days to sync backwards")
    days_forward: Optional[int] = Field(30, description="Days to sync forward")


class CalendarSyncResponse(BaseModel):
    status: str
    sync_window: Optional[Dict[str, str]] = {}
    summary: Optional[Dict[str, Any]] = {}
    created_meetings: Optional[List[Dict[str, Any]]] = []
    updated_meetings: Optional[List[Dict[str, Any]]] = []
    deleted_meetings: Optional[List[Dict[str, Any]]] = []
    conflicts_resolved: Optional[List[Dict[str, Any]]] = []
    ai_decisions: Optional[List[Dict[str, Any]]] = []


class FreeBusyResponse(BaseModel):
    time_min: str
    time_max: str
    calendars: Dict[str, Any]
    groups: Optional[Dict[str, Any]] = {}
    errors: Optional[List[Dict[str, Any]]] = []


class EventResponseRequest(BaseModel):
    response_status: str = Field(..., description="accepted, declined, or tentative")
    comment: Optional[str] = Field(None, description="Optional comment")


# Analytics Schemas
class WeeklyReportResponse(BaseModel):
    period: Dict[str, Any]
    summary: Dict[str, Any]
    patterns: Dict[str, Any]
    ai_insights: Dict[str, Any]
    recommendations: List[str]


class MonthlyReportResponse(BaseModel):
    period: Dict[str, Any]
    summary: Dict[str, Any]
    weekly_breakdown: List[Dict[str, Any]]
    trends: Dict[str, Any]
    efficiency: Dict[str, Any]


# Conflict Management Schemas
class ConflictAnalysisResponse(BaseModel):
    total_conflicts: int
    conflicts: List[Dict[str, Any]]
    resolution_plans: List[Dict[str, Any]]


class ConflictResolutionRequest(BaseModel):
    strategy: str
    approve_execution: bool = False
    custom_parameters: Optional[Dict[str, Any]] = {}


class ConflictResolutionResponse(BaseModel):
    conflict_id: str
    status: str
    message: str
    executed_actions: List[Dict[str, Any]]
    estimated_completion_time: Optional[str] = None


# Focus Time Schemas
class FocusTimeBlock(BaseModel):
    start_time: str
    end_time: str
    focus_type: str = Field("Deep Work", description="Type of focus work")


class FocusTimeRequest(BaseModel):
    focus_blocks: List[FocusTimeBlock]


class FocusTimeResponse(BaseModel):
    created_focus_blocks: int
    focus_event_ids: List[str]
    message: str