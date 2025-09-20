from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    preferences: Optional[Dict[str, Any]] = None


# Properties to receive on creation
class UserCreate(UserBase):
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None


# Properties to receive on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


# Properties stored in database
class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class User(UserInDB):
    pass