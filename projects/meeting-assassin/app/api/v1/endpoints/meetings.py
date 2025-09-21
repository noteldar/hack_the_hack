"""
Meeting management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.database import get_db
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus, MeetingPriority
from app.schemas.meeting import (
    MeetingCreate, MeetingResponse, MeetingUpdate,
    MeetingAnalysisResponse, MeetingListResponse
)
from app.services.auth import AuthService
from app.services.meeting import MeetingService
from app.services.ai_avatar import AIAvatarService
from app.core.websocket import WebSocketManager

router = APIRouter()
auth_service = AuthService()
meeting_service = MeetingService()
ai_service = AIAvatarService()
websocket_manager = WebSocketManager()


@router.get("/", response_model=MeetingListResponse)
async def get_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[MeetingStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's meetings with filtering and pagination"""
    try:
        query = select(Meeting).where(Meeting.user_id == current_user.id)

        # Apply filters
        if status:
            query = query.where(Meeting.status == status)

        if start_date:
            query = query.where(Meeting.start_time >= start_date)

        if end_date:
            query = query.where(Meeting.end_time <= end_date)

        # Order by start time
        query = query.order_by(Meeting.start_time).offset(skip).limit(limit)

        result = await db.execute(query)
        meetings = result.scalars().all()

        # Get total count
        count_query = select(Meeting).where(Meeting.user_id == current_user.id)
        if status:
            count_query = count_query.where(Meeting.status == status)
        if start_date:
            count_query = count_query.where(Meeting.start_time >= start_date)
        if end_date:
            count_query = count_query.where(Meeting.end_time <= end_date)

        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return MeetingListResponse(
            meetings=[MeetingResponse.from_orm(meeting) for meeting in meetings],
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch meetings: {str(e)}"
        )


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific meeting"""
    meeting = await db.get(Meeting, meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return MeetingResponse.from_orm(meeting)


@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting_data: MeetingCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new meeting"""
    try:
        # Calculate duration
        duration = (meeting_data.end_time - meeting_data.start_time).total_seconds() / 60

        meeting = Meeting(
            user_id=current_user.id,
            title=meeting_data.title,
            description=meeting_data.description,
            location=meeting_data.location,
            meeting_link=meeting_data.meeting_link,
            start_time=meeting_data.start_time,
            end_time=meeting_data.end_time,
            timezone=current_user.timezone,
            duration_minutes=int(duration),
            organizer_email=current_user.email,
            attendees=meeting_data.attendees,
            required_attendees=meeting_data.required_attendees,
            optional_attendees=meeting_data.optional_attendees,
            priority=meeting_data.priority or MeetingPriority.MEDIUM,
            meeting_type=meeting_data.meeting_type
        )

        db.add(meeting)
        await db.commit()
        await db.refresh(meeting)

        # Queue AI analysis
        background_tasks.add_task(
            ai_service.analyze_meeting,
            meeting.id,
            current_user.id
        )

        # Send WebSocket update
        await websocket_manager.send_meeting_update(
            str(current_user.id),
            {
                "type": "meeting_created",
                "meeting_id": meeting.id,
                "title": meeting.title,
                "start_time": meeting.start_time.isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return MeetingResponse.from_orm(meeting)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create meeting: {str(e)}"
        )


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a meeting"""
    meeting = await db.get(Meeting, meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    try:
        # Update fields
        update_data = meeting_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)

        # Recalculate duration if times changed
        if meeting_update.start_time or meeting_update.end_time:
            duration = (meeting.end_time - meeting.start_time).total_seconds() / 60
            meeting.duration_minutes = int(duration)

        await db.commit()
        await db.refresh(meeting)

        # Queue AI re-analysis
        background_tasks.add_task(
            ai_service.analyze_meeting,
            meeting.id,
            current_user.id
        )

        # Send WebSocket update
        await websocket_manager.send_meeting_update(
            str(current_user.id),
            {
                "type": "meeting_updated",
                "meeting_id": meeting.id,
                "title": meeting.title,
                "changes": list(update_data.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return MeetingResponse.from_orm(meeting)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update meeting: {str(e)}"
        )


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a meeting"""
    meeting = await db.get(Meeting, meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    try:
        await db.delete(meeting)
        await db.commit()

        # Send WebSocket update
        await websocket_manager.send_meeting_update(
            str(current_user.id),
            {
                "type": "meeting_deleted",
                "meeting_id": meeting_id,
                "title": meeting.title,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return {"message": "Meeting deleted successfully", "meeting_id": meeting_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete meeting: {str(e)}"
        )


@router.get("/{meeting_id}/analysis", response_model=MeetingAnalysisResponse)
async def get_meeting_analysis(
    meeting_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI analysis for a meeting"""
    meeting = await db.get(Meeting, meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    analysis = meeting.get_ai_decision_data()

    return MeetingAnalysisResponse(
        meeting_id=meeting_id,
        importance_score=analysis.get("importance_score"),
        conflict_score=analysis.get("conflict_score"),
        productivity_impact=analysis.get("productivity_impact"),
        ai_decision=analysis.get("decision"),
        decision_confidence=analysis.get("confidence"),
        reasoning=analysis.get("reasoning"),
        last_analyzed=meeting.last_ai_analysis
    )


@router.post("/{meeting_id}/analyze")
async def analyze_meeting(
    meeting_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger AI analysis for a meeting"""
    meeting = await db.get(Meeting, meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # Queue AI analysis
    background_tasks.add_task(
        ai_service.analyze_meeting,
        meeting_id,
        current_user.id
    )

    return {"message": "Analysis queued", "meeting_id": meeting_id}


@router.get("/today/dashboard")
async def today_dashboard(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get today's meeting dashboard"""
    try:
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        # Get today's meetings
        query = select(Meeting).where(
            and_(
                Meeting.user_id == current_user.id,
                Meeting.start_time >= start_of_day,
                Meeting.start_time <= end_of_day
            )
        ).order_by(Meeting.start_time)

        result = await db.execute(query)
        meetings = result.scalars().all()

        # Calculate metrics
        total_meetings = len(meetings)
        total_duration = sum(m.duration_minutes or 0 for m in meetings)
        upcoming_meetings = [m for m in meetings if m.start_time > datetime.utcnow()]
        completed_meetings = [m for m in meetings if m.status == MeetingStatus.COMPLETED]

        # AI decisions summary
        ai_decisions = {}
        for meeting in meetings:
            if meeting.ai_decision:
                ai_decisions[meeting.ai_decision] = ai_decisions.get(meeting.ai_decision, 0) + 1

        return {
            "date": today.isoformat(),
            "total_meetings": total_meetings,
            "total_duration_minutes": total_duration,
            "total_duration_hours": total_duration / 60,
            "upcoming_count": len(upcoming_meetings),
            "completed_count": len(completed_meetings),
            "ai_decisions_summary": ai_decisions,
            "meetings": [MeetingResponse.from_orm(m) for m in meetings],
            "next_meeting": MeetingResponse.from_orm(upcoming_meetings[0]) if upcoming_meetings else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {str(e)}"
        )


@router.get("/conflicts/detect")
async def detect_conflicts(
    days_ahead: int = Query(7, ge=1, le=30),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect scheduling conflicts"""
    try:
        conflicts = await meeting_service.detect_conflicts(
            current_user.id, days_ahead, db
        )

        return {
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "scan_period_days": days_ahead
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect conflicts: {str(e)}"
        )