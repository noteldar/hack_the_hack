from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.deps import get_current_active_user
from app.models.user import User
from app.models.meeting import MeetingStatus
from app.schemas.meeting import Meeting, MeetingCreate, MeetingUpdate
from app.services.meeting import MeetingService

router = APIRouter()


@router.post("/", response_model=Meeting)
async def create_meeting(
    meeting_create: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new meeting"""
    meeting_service = MeetingService(db)
    return await meeting_service.create_meeting(current_user.id, meeting_create)


@router.get("/", response_model=List[Meeting])
async def get_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[MeetingStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's meetings"""
    meeting_service = MeetingService(db)
    return await meeting_service.get_user_meetings(
        current_user.id, skip=skip, limit=limit, status=status
    )


@router.get("/{meeting_id}", response_model=Meeting)
async def get_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific meeting"""
    meeting_service = MeetingService(db)
    meeting = await meeting_service.get_meeting_by_id(meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return meeting


@router.patch("/{meeting_id}", response_model=Meeting)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a meeting"""
    meeting_service = MeetingService(db)
    meeting = await meeting_service.get_meeting_by_id(meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return await meeting_service.update_meeting(meeting_id, meeting_update)


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a meeting"""
    meeting_service = MeetingService(db)
    meeting = await meeting_service.get_meeting_by_id(meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    await meeting_service.delete_meeting(meeting_id)
    return {"message": "Meeting deleted successfully"}


@router.post("/{meeting_id}/prepare")
async def prepare_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger AI meeting preparation"""
    meeting_service = MeetingService(db)
    meeting = await meeting_service.get_meeting_by_id(meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # This would trigger a background job for AI meeting preparation
    # For now, return a success message
    return {"message": "Meeting preparation started", "meeting_id": meeting_id}