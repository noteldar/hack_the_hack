from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.task import TaskStatus, TaskPriority


# Shared properties
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=1)  # in minutes
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


# Properties to receive on creation
class TaskCreate(TaskBase):
    meeting_id: Optional[int] = None
    email_id: Optional[int] = None


# Properties to receive on update
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


# Properties stored in database
class TaskInDB(TaskBase):
    id: int
    status: TaskStatus
    extracted_from_email: bool
    extraction_confidence: Optional[int] = None
    ai_generated: bool
    user_id: int
    meeting_id: Optional[int] = None
    email_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class Task(TaskInDB):
    pass