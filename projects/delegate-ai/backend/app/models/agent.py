from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class AgentType(PyEnum):
    CALENDAR_MANAGER = "calendar_manager"
    EMAIL_PROCESSOR = "email_processor"
    MEETING_PREPARER = "meeting_preparer"
    TASK_ORGANIZER = "task_organizer"
    SCHEDULER = "scheduler"
    RESEARCH_ASSISTANT = "research_assistant"


class AgentStatus(PyEnum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


class ActivityType(PyEnum):
    EMAIL_PROCESSED = "email_processed"
    TASK_CREATED = "task_created"
    MEETING_PREPARED = "meeting_prepared"
    CALENDAR_UPDATED = "calendar_updated"
    RESEARCH_COMPLETED = "research_completed"
    NOTIFICATION_SENT = "notification_sent"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    description = Column(Text, nullable=True)

    # Agent configuration
    config = Column(Text, nullable=True)  # JSON configuration
    is_enabled = Column(Boolean, default=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)

    # Performance metrics
    total_tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # 0.0 to 1.0
    average_execution_time = Column(Float, nullable=True)  # in seconds

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="agents")
    activities = relationship("AgentActivity", back_populates="agent")


class AgentActivity(Base):
    __tablename__ = "agent_activities"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(Enum(ActivityType), nullable=False)
    description = Column(String, nullable=False)
    details = Column(Text, nullable=True)  # JSON details

    # Execution metadata
    execution_time = Column(Float, nullable=True)  # in seconds
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Related entities
    related_email_id = Column(Integer, nullable=True)
    related_task_id = Column(Integer, nullable=True)
    related_meeting_id = Column(Integer, nullable=True)

    # Agent relationship
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="activities")