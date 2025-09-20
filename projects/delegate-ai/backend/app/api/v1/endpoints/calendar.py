from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.deps import get_current_active_user
from app.models.user import User
from app.schemas.meeting import Meeting
from app.services.calendar import CalendarService

router = APIRouter()


@router.get("/events", response_model=List[Meeting])
async def get_calendar_events(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get calendar events/meetings for date range"""
    calendar_service = CalendarService(db)
    return await calendar_service.get_calendar_events(
        current_user.id, start_date=start_date, end_date=end_date
    )


@router.post("/sync")
async def sync_calendar(
    provider: str = Query(..., regex="^(google|microsoft)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sync calendar with external provider"""
    calendar_service = CalendarService(db)

    # This would integrate with Google Calendar or Microsoft Graph API
    # For now, return a placeholder response
    return {
        "message": f"Calendar sync with {provider} started",
        "user_id": current_user.id,
        "provider": provider
    }


@router.get("/availability")
async def get_availability(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check availability for time slot"""
    calendar_service = CalendarService(db)
    is_available = await calendar_service.check_availability(
        current_user.id, start_time, end_time
    )

    return {
        "start_time": start_time,
        "end_time": end_time,
        "is_available": is_available
    }


@router.post("/find-slots")
async def find_available_slots(
    duration_minutes: int = Query(..., ge=15, le=480),
    start_date: date = Query(...),
    end_date: date = Query(...),
    working_hours_start: int = Query(9, ge=0, le=23),
    working_hours_end: int = Query(17, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Find available time slots for scheduling"""
    calendar_service = CalendarService(db)
    slots = await calendar_service.find_available_slots(
        user_id=current_user.id,
        duration_minutes=duration_minutes,
        start_date=start_date,
        end_date=end_date,
        working_hours_start=working_hours_start,
        working_hours_end=working_hours_end
    )

    return {
        "available_slots": slots,
        "duration_minutes": duration_minutes,
        "date_range": {"start": start_date, "end": end_date}
    }