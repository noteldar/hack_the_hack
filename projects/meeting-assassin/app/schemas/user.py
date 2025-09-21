"""
User schemas
"""

from pydantic import BaseModel
from typing import Optional


class UserUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPreferences(BaseModel):
    timezone: str = "UTC"
    work_hours_start: int = 9
    work_hours_end: int = 17
    preferred_meeting_duration: int = 30
    avatar_personality: str = "professional"
    ai_decision_autonomy: float = 0.5
    auto_decline_conflicts: bool = False
    auto_suggest_reschedule: bool = True
    focus_time_blocks: int = 2
    focus_block_duration: int = 120
    break_duration: int = 15


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    avatar_url: Optional[str] = None
    timezone: str
    avatar_personality: str

    class Config:
        from_attributes = True