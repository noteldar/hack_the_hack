"""
Meeting model for MeetingAssassin
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User


class MeetingStatus(str, Enum):
    """Meeting status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class MeetingPriority(str, Enum):
    """Meeting priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIDecisionType(str, Enum):
    """Types of AI decisions for meetings"""
    AUTO_ACCEPT = "auto_accept"
    AUTO_DECLINE = "auto_decline"
    SUGGEST_RESCHEDULE = "suggest_reschedule"
    REQUEST_MORE_INFO = "request_more_info"
    DELEGATE = "delegate"


class Meeting(Base):
    """Meeting model with AI decision tracking"""

    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Google Calendar integration
    google_event_id = Column(String, unique=True, index=True)
    calendar_id = Column(String, default="primary")

    # Meeting details
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    meeting_link = Column(String)

    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String, default="UTC")
    duration_minutes = Column(Integer)

    # Participants
    organizer_email = Column(String)
    attendees = Column(JSON)  # List of attendee emails
    required_attendees = Column(JSON)  # Required participants
    optional_attendees = Column(JSON)  # Optional participants

    # Meeting metadata
    status = Column(String, default=MeetingStatus.SCHEDULED)
    priority = Column(String, default=MeetingPriority.MEDIUM)
    meeting_type = Column(String)  # "standup", "review", "planning", etc.
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(Text)

    # AI Analysis
    ai_importance_score = Column(Float)  # 0.0 to 1.0
    ai_conflict_score = Column(Float)    # 0.0 to 1.0 (higher = more conflicts)
    ai_productivity_impact = Column(Float)  # -1.0 to 1.0
    ai_decision = Column(String)  # AIDecisionType
    ai_decision_confidence = Column(Float)  # 0.0 to 1.0
    ai_decision_reasoning = Column(Text)

    # Meeting outcomes
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    was_productive = Column(Boolean)
    productivity_score = Column(Float)  # User or AI rated
    action_items = Column(JSON)  # List of action items
    meeting_notes = Column(Text)

    # Optimization data
    optimal_time_slot = Column(DateTime)  # Suggested by genetic algorithm
    optimization_score = Column(Float)    # Fitness score from genetic algorithm
    rescheduling_suggestions = Column(JSON)  # Alternative time slots

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_ai_analysis = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="meetings")

    def __repr__(self):
        return f"<Meeting(id={self.id}, title='{self.title}', start='{self.start_time}')>"

    @property
    def duration_hours(self) -> float:
        """Calculate meeting duration in hours"""
        if self.duration_minutes:
            return self.duration_minutes / 60
        return 0

    @property
    def is_past(self) -> bool:
        """Check if meeting is in the past"""
        return self.end_time < datetime.utcnow()

    @property
    def is_today(self) -> bool:
        """Check if meeting is today"""
        return self.start_time.date() == datetime.utcnow().date()

    @property
    def conflicts_with_focus_time(self) -> bool:
        """Check if meeting conflicts with typical focus time"""
        # Assuming focus time is 9-11 AM and 2-4 PM
        hour = self.start_time.hour
        return (9 <= hour <= 11) or (14 <= hour <= 16)

    def calculate_conflict_score(self, other_meetings: List["Meeting"]) -> float:
        """Calculate conflict score based on overlapping meetings"""
        conflicts = 0
        total_overlap_minutes = 0

        for other in other_meetings:
            if other.id == self.id:
                continue

            # Check for time overlap
            if (self.start_time < other.end_time and
                self.end_time > other.start_time):
                conflicts += 1
                # Calculate overlap duration
                overlap_start = max(self.start_time, other.start_time)
                overlap_end = min(self.end_time, other.end_time)
                overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                total_overlap_minutes += overlap_minutes

        # Normalize conflict score (0.0 to 1.0)
        if not other_meetings:
            return 0.0

        conflict_ratio = conflicts / len(other_meetings)
        overlap_penalty = min(total_overlap_minutes / (24 * 60), 1.0)  # Cap at 1 day

        return min(conflict_ratio + overlap_penalty, 1.0)

    def get_ai_decision_data(self) -> Dict[str, Any]:
        """Get AI decision information"""
        return {
            "decision": self.ai_decision,
            "confidence": self.ai_decision_confidence,
            "reasoning": self.ai_decision_reasoning,
            "importance_score": self.ai_importance_score,
            "conflict_score": self.ai_conflict_score,
            "productivity_impact": self.ai_productivity_impact
        }

    def to_calendar_event(self) -> Dict[str, Any]:
        """Convert to Google Calendar event format"""
        return {
            "summary": self.title,
            "description": self.description,
            "location": self.location,
            "start": {
                "dateTime": self.start_time.isoformat(),
                "timeZone": self.timezone
            },
            "end": {
                "dateTime": self.end_time.isoformat(),
                "timeZone": self.timezone
            },
            "attendees": [{"email": email} for email in (self.attendees or [])],
            "conferenceData": {
                "createRequest": {"requestId": f"meeting-{self.id}"}
            } if self.meeting_link else None
        }