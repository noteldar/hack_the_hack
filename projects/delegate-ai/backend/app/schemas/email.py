from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.email import EmailStatus, EmailProvider


# Shared properties
class EmailBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=500)
    sender_email: EmailStr
    sender_name: Optional[str] = None
    recipient_emails: List[EmailStr]
    cc_emails: Optional[List[EmailStr]] = None
    bcc_emails: Optional[List[EmailStr]] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    received_at: datetime


# Properties to receive on creation
class EmailCreate(EmailBase):
    message_id: str
    thread_id: Optional[str] = None
    provider: EmailProvider = EmailProvider.GMAIL


# Properties to receive on update
class EmailUpdate(BaseModel):
    status: Optional[EmailStatus] = None
    is_important: Optional[bool] = None
    requires_response: Optional[bool] = None
    ai_summary: Optional[str] = None
    ai_sentiment: Optional[str] = None
    ai_category: Optional[str] = None
    ai_extracted_tasks: Optional[List[Dict[str, Any]]] = None
    ai_confidence: Optional[int] = Field(None, ge=0, le=100)
    processed_at: Optional[datetime] = None


# Properties stored in database
class EmailInDB(EmailBase):
    id: int
    message_id: str
    thread_id: Optional[str] = None
    status: EmailStatus
    provider: EmailProvider
    is_important: bool
    requires_response: bool
    ai_summary: Optional[str] = None
    ai_sentiment: Optional[str] = None
    ai_category: Optional[str] = None
    ai_extracted_tasks: Optional[List[Dict[str, Any]]] = None
    ai_confidence: Optional[int] = None
    processed_at: Optional[datetime] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class Email(EmailInDB):
    pass