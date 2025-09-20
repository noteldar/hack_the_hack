from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.models.email import Email, EmailStatus
from app.schemas.email import EmailCreate, EmailUpdate


class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_email(self, user_id: int, email_create: EmailCreate) -> Email:
        """Create/import a new email"""
        # Check if email already exists
        result = await self.db.execute(
            select(Email).where(Email.message_id == email_create.message_id)
        )
        existing_email = result.scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        email = Email(
            message_id=email_create.message_id,
            thread_id=email_create.thread_id,
            subject=email_create.subject,
            sender_email=email_create.sender_email,
            sender_name=email_create.sender_name,
            recipient_emails=email_create.recipient_emails,
            cc_emails=email_create.cc_emails,
            bcc_emails=email_create.bcc_emails,
            body_text=email_create.body_text,
            body_html=email_create.body_html,
            attachments=email_create.attachments,
            received_at=email_create.received_at,
            provider=email_create.provider,
            user_id=user_id,
            status=EmailStatus.UNREAD
        )

        self.db.add(email)
        await self.db.commit()
        await self.db.refresh(email)
        return email

    async def get_email_by_id(self, email_id: int) -> Optional[Email]:
        """Get email by ID"""
        result = await self.db.execute(select(Email).where(Email.id == email_id))
        return result.scalar_one_or_none()

    async def get_user_emails(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[EmailStatus] = None,
        is_important: Optional[bool] = None
    ) -> List[Email]:
        """Get user's emails with filtering"""
        query = select(Email).where(Email.user_id == user_id)

        if status:
            query = query.where(Email.status == status)
        if is_important is not None:
            query = query.where(Email.is_important == is_important)

        query = query.offset(skip).limit(limit).order_by(Email.received_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_email(self, email_id: int, email_update: EmailUpdate) -> Email:
        """Update email status or AI analysis"""
        # Get existing email
        result = await self.db.execute(select(Email).where(Email.id == email_id))
        email = result.scalar_one_or_none()

        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

        # Update fields
        update_data = email_update.model_dump(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(Email)
                .where(Email.id == email_id)
                .values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(email)

        return email