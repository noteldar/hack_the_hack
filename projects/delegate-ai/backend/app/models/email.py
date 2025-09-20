from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class EmailStatus(PyEnum):
    UNREAD = "unread"
    READ = "read"
    PROCESSED = "processed"
    ARCHIVED = "archived"


class EmailProvider(PyEnum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    OTHER = "other"


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    # Email metadata
    message_id = Column(String, unique=True, nullable=False)  # Unique email ID
    thread_id = Column(String, nullable=True)  # Email thread ID
    subject = Column(String, nullable=False)
    sender_email = Column(String, nullable=False)
    sender_name = Column(String, nullable=True)
    recipient_emails = Column(Text, nullable=False)  # JSON array
    cc_emails = Column(Text, nullable=True)  # JSON array
    bcc_emails = Column(Text, nullable=True)  # JSON array

    # Email content
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    attachments = Column(Text, nullable=True)  # JSON array of attachment metadata

    # Email status and processing
    status = Column(Enum(EmailStatus), default=EmailStatus.UNREAD)
    provider = Column(Enum(EmailProvider), default=EmailProvider.GMAIL)
    is_important = Column(Boolean, default=False)
    requires_response = Column(Boolean, default=False)

    # AI processing results
    ai_summary = Column(Text, nullable=True)
    ai_sentiment = Column(String, nullable=True)  # positive, negative, neutral
    ai_category = Column(String, nullable=True)  # meeting, task, information, etc.
    ai_extracted_tasks = Column(Text, nullable=True)  # JSON array
    ai_confidence = Column(Integer, nullable=True)  # 0-100

    # Timing
    received_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="emails")
    tasks = relationship("Task", back_populates="email")