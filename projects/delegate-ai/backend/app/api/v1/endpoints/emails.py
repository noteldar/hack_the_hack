from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.deps import get_current_active_user
from app.models.user import User
from app.models.email import EmailStatus
from app.schemas.email import Email, EmailCreate, EmailUpdate
from app.services.email import EmailService

router = APIRouter()


@router.post("/", response_model=Email)
async def create_email(
    email_create: EmailCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create/import a new email"""
    email_service = EmailService(db)
    return await email_service.create_email(current_user.id, email_create)


@router.get("/", response_model=List[Email])
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[EmailStatus] = None,
    is_important: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's emails with filtering"""
    email_service = EmailService(db)
    return await email_service.get_user_emails(
        current_user.id, skip=skip, limit=limit, status=status, is_important=is_important
    )


@router.get("/{email_id}", response_model=Email)
async def get_email(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific email"""
    email_service = EmailService(db)
    email = await email_service.get_email_by_id(email_id)

    if not email or email.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    return email


@router.patch("/{email_id}", response_model=Email)
async def update_email(
    email_id: int,
    email_update: EmailUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update email status or AI analysis"""
    email_service = EmailService(db)
    email = await email_service.get_email_by_id(email_id)

    if not email or email.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    return await email_service.update_email(email_id, email_update)


@router.post("/{email_id}/process")
async def process_email(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger AI processing for email"""
    email_service = EmailService(db)
    email = await email_service.get_email_by_id(email_id)

    if not email or email.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    # This would trigger background job for AI processing
    # For now, return success message
    return {"message": "Email processing started", "email_id": email_id}


@router.post("/{email_id}/extract-tasks")
async def extract_tasks_from_email(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Extract tasks from email using AI"""
    email_service = EmailService(db)
    email = await email_service.get_email_by_id(email_id)

    if not email or email.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    # This would use AI to extract tasks from email content
    # For now, return placeholder response
    return {
        "message": "Task extraction completed",
        "email_id": email_id,
        "extracted_tasks": []
    }