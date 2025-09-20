from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.agent import AgentType, AgentStatus, ActivityType


# Agent schemas
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    agent_type: AgentType
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_enabled: bool = True


# Properties to receive on creation
class AgentCreate(AgentBase):
    pass


# Properties to receive on update
class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    status: Optional[AgentStatus] = None


# Properties stored in database
class AgentInDB(AgentBase):
    id: int
    status: AgentStatus
    total_tasks_completed: int
    success_rate: float
    average_execution_time: Optional[float] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class Agent(AgentInDB):
    pass


# Agent Activity schemas
class AgentActivityBase(BaseModel):
    activity_type: ActivityType
    description: str = Field(..., min_length=1, max_length=200)
    details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = Field(None, ge=0)
    success: bool = True
    error_message: Optional[str] = None


# Properties to receive on creation
class AgentActivityCreate(AgentActivityBase):
    related_email_id: Optional[int] = None
    related_task_id: Optional[int] = None
    related_meeting_id: Optional[int] = None


# Properties stored in database and returned to client
class AgentActivity(AgentActivityBase):
    id: int
    related_email_id: Optional[int] = None
    related_task_id: Optional[int] = None
    related_meeting_id: Optional[int] = None
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True