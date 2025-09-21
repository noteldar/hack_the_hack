"""
Productivity metrics model for MeetingAssassin
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
from typing import TYPE_CHECKING, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User


class MetricType(str, Enum):
    """Types of productivity metrics"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MEETING_SPECIFIC = "meeting_specific"


class ProductivityMetric(Base):
    """Productivity metrics tracking"""

    __tablename__ = "productivity_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Metric metadata
    metric_type = Column(String, nullable=False)  # MetricType
    date = Column(DateTime, nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)

    # Time-based metrics
    total_meeting_time = Column(Float, default=0.0)  # Hours
    focus_time_achieved = Column(Float, default=0.0)  # Hours
    interruption_count = Column(Integer, default=0)
    context_switches = Column(Integer, default=0)

    # Meeting-specific metrics
    meetings_attended = Column(Integer, default=0)
    meetings_declined = Column(Integer, default=0)
    meetings_rescheduled = Column(Integer, default=0)
    meetings_auto_managed = Column(Integer, default=0)

    # Quality metrics
    average_meeting_rating = Column(Float)  # 1.0 to 5.0
    productive_meetings_ratio = Column(Float)  # 0.0 to 1.0
    on_time_attendance = Column(Float)  # 0.0 to 1.0
    preparation_score = Column(Float)  # 0.0 to 1.0

    # AI effectiveness metrics
    ai_decisions_accepted = Column(Integer, default=0)
    ai_decisions_rejected = Column(Integer, default=0)
    ai_accuracy_score = Column(Float)  # 0.0 to 1.0
    time_saved_by_ai = Column(Float)  # Minutes

    # Calendar optimization metrics
    calendar_optimization_score = Column(Float)  # 0.0 to 1.0
    schedule_adherence = Column(Float)  # 0.0 to 1.0
    optimal_slots_used = Column(Integer, default=0)
    suboptimal_slots_used = Column(Integer, default=0)

    # Detailed data
    meeting_breakdown = Column(JSON)  # Meeting types and counts
    productivity_patterns = Column(JSON)  # Time-based productivity data
    ai_decision_breakdown = Column(JSON)  # AI decision statistics
    optimization_history = Column(JSON)  # Calendar optimization results

    # Goals and targets
    focus_time_goal = Column(Float)  # Hours
    meeting_limit_goal = Column(Integer)  # Max meetings per day
    productivity_target = Column(Float)  # Target score

    # Calculated scores
    overall_productivity_score = Column(Float)  # 0.0 to 100.0
    meeting_efficiency_score = Column(Float)  # 0.0 to 100.0
    ai_collaboration_score = Column(Float)  # 0.0 to 100.0

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="productivity_metrics")

    def __repr__(self):
        return f"<ProductivityMetric(id={self.id}, user_id={self.user_id}, type='{self.metric_type}', date='{self.date}')>"

    def calculate_productivity_score(self) -> float:
        """Calculate overall productivity score (0-100)"""
        scores = []

        # Focus time score (40% weight)
        if self.focus_time_goal and self.focus_time_goal > 0:
            focus_score = min((self.focus_time_achieved / self.focus_time_goal) * 100, 100)
            scores.append(focus_score * 0.4)

        # Meeting efficiency score (30% weight)
        if self.meetings_attended > 0:
            efficiency = (self.productive_meetings_ratio or 0) * 100
            scores.append(efficiency * 0.3)

        # AI collaboration score (20% weight)
        if self.ai_decisions_accepted + self.ai_decisions_rejected > 0:
            ai_score = (self.ai_accuracy_score or 0) * 100
            scores.append(ai_score * 0.2)

        # Schedule optimization score (10% weight)
        optimization_score = (self.calendar_optimization_score or 0) * 100
        scores.append(optimization_score * 0.1)

        return sum(scores) if scores else 0.0

    def get_meeting_stats(self) -> Dict[str, Any]:
        """Get meeting-related statistics"""
        total_meetings = (
            self.meetings_attended +
            self.meetings_declined +
            self.meetings_rescheduled
        )

        return {
            "total_meetings": total_meetings,
            "attended": self.meetings_attended,
            "declined": self.meetings_declined,
            "rescheduled": self.meetings_rescheduled,
            "auto_managed": self.meetings_auto_managed,
            "attendance_rate": self.meetings_attended / total_meetings if total_meetings > 0 else 0,
            "ai_automation_rate": self.meetings_auto_managed / total_meetings if total_meetings > 0 else 0,
            "average_rating": self.average_meeting_rating,
            "productive_ratio": self.productive_meetings_ratio
        }

    def get_ai_performance(self) -> Dict[str, Any]:
        """Get AI performance metrics"""
        total_decisions = self.ai_decisions_accepted + self.ai_decisions_rejected

        return {
            "total_decisions": total_decisions,
            "accepted": self.ai_decisions_accepted,
            "rejected": self.ai_decisions_rejected,
            "acceptance_rate": self.ai_decisions_accepted / total_decisions if total_decisions > 0 else 0,
            "accuracy_score": self.ai_accuracy_score,
            "time_saved_minutes": self.time_saved_by_ai,
            "collaboration_score": self.ai_collaboration_score
        }

    def get_focus_time_analysis(self) -> Dict[str, Any]:
        """Get focus time analysis"""
        return {
            "achieved_hours": self.focus_time_achieved,
            "goal_hours": self.focus_time_goal,
            "achievement_rate": (self.focus_time_achieved / self.focus_time_goal * 100) if self.focus_time_goal else 0,
            "interruptions": self.interruption_count,
            "context_switches": self.context_switches,
            "avg_focus_session": self.focus_time_achieved / max(1, self.interruption_count + 1)
        }

    def update_with_meeting_data(self, meeting_data: Dict[str, Any]):
        """Update metrics with new meeting data"""
        # Update meeting counts
        if meeting_data.get("attended"):
            self.meetings_attended += 1
        if meeting_data.get("declined"):
            self.meetings_declined += 1
        if meeting_data.get("rescheduled"):
            self.meetings_rescheduled += 1
        if meeting_data.get("auto_managed"):
            self.meetings_auto_managed += 1

        # Update time metrics
        if meeting_data.get("duration_hours"):
            self.total_meeting_time += meeting_data["duration_hours"]

        # Update quality metrics
        if meeting_data.get("rating"):
            current_total = (self.average_meeting_rating or 0) * (self.meetings_attended - 1)
            self.average_meeting_rating = (current_total + meeting_data["rating"]) / self.meetings_attended

        # Update AI metrics
        if meeting_data.get("ai_decision_accepted"):
            self.ai_decisions_accepted += 1
        if meeting_data.get("ai_decision_rejected"):
            self.ai_decisions_rejected += 1

        # Recalculate scores
        self.overall_productivity_score = self.calculate_productivity_score()
        self.updated_at = func.now()

    @classmethod
    def create_daily_metric(cls, user_id: int, date: datetime) -> "ProductivityMetric":
        """Create a new daily productivity metric"""
        return cls(
            user_id=user_id,
            metric_type=MetricType.DAILY,
            date=date,
            period_start=date.replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=date.replace(hour=23, minute=59, second=59, microsecond=999999)
        )

    @classmethod
    def create_weekly_metric(cls, user_id: int, week_start: datetime) -> "ProductivityMetric":
        """Create a new weekly productivity metric"""
        week_end = week_start + timedelta(days=6)
        return cls(
            user_id=user_id,
            metric_type=MetricType.WEEKLY,
            date=week_start,
            period_start=week_start,
            period_end=week_end
        )