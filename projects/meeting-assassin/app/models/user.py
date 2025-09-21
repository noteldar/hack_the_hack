"""
User model for MeetingAssassin
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.productivity import ProductivityMetric


class User(Base):
    """User model with Google OAuth integration"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    google_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    avatar_url = Column(String)

    # Google Calendar integration
    calendar_connected = Column(Boolean, default=False)
    calendar_connected_at = Column(DateTime)
    google_calendar_tokens = Column(Text)  # JSON string of OAuth tokens

    # Legacy OAuth tokens (deprecated)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)

    # User preferences
    timezone = Column(String, default="UTC")
    work_hours_start = Column(Integer, default=9)  # 9 AM
    work_hours_end = Column(Integer, default=17)   # 5 PM
    preferred_meeting_duration = Column(Integer, default=30)  # 30 minutes

    # AI Avatar settings
    avatar_personality = Column(String, default="professional")
    ai_decision_autonomy = Column(Float, default=0.5)  # 0.0 to 1.0
    auto_decline_conflicts = Column(Boolean, default=False)
    auto_suggest_reschedule = Column(Boolean, default=True)
    autonomous_mode = Column(Boolean, default=False)  # Enable full autonomous operation

    # Productivity preferences
    focus_time_blocks = Column(Integer, default=2)  # Number of focus blocks per day
    focus_block_duration = Column(Integer, default=120)  # Minutes
    break_duration = Column(Integer, default=15)  # Minutes
    max_meetings_per_day = Column(Integer, default=6)  # Maximum meetings per day
    min_buffer_minutes = Column(Integer, default=15)  # Minimum buffer between meetings
    preferences = Column(JSON)  # Additional user preferences as JSON

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)

    # Relationships
    meetings = relationship("Meeting", back_populates="user")
    productivity_metrics = relationship("ProductivityMetric", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

    @property
    def is_authenticated(self) -> bool:
        """Check if user has valid tokens"""
        return bool(self.calendar_connected and self.google_calendar_tokens)

    @property
    def is_admin(self) -> bool:
        """Check if user is admin (simple implementation)"""
        return self.email.endswith('@meetingassassin.com')

    @property
    def work_hours_duration(self) -> int:
        """Calculate work hours duration in hours"""
        return self.work_hours_end - self.work_hours_start

    def get_avatar_config(self) -> dict:
        """Get AI avatar configuration"""
        return {
            "personality": self.avatar_personality,
            "autonomy": self.ai_decision_autonomy,
            "auto_decline_conflicts": self.auto_decline_conflicts,
            "auto_suggest_reschedule": self.auto_suggest_reschedule,
            "timezone": self.timezone
        }