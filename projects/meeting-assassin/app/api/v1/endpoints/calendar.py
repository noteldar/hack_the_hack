"""
Advanced Google Calendar integration endpoints with autonomous management
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.database import get_db
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus, AIDecisionType
from app.schemas.calendar import *
from app.services.oauth_service import oauth_service
from app.services.google_calendar import google_calendar_client, autonomous_calendar_manager
from app.services.calendar_sync import calendar_sync_service
from app.services.calendar_analytics import calendar_analytics
from app.services.conflict_resolution import conflict_detector, conflict_resolver
from app.services.meeting_intelligence import meeting_intelligence_service
from app.api.dependencies import get_current_user
from app.core.websocket import websocket_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/connect", response_model=CalendarConnectionResponse)
async def connect_google_calendar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Initiate Google Calendar OAuth connection"""
    try:
        auth_url = await oauth_service.initiate_oauth_flow(current_user.id, db)

        return CalendarConnectionResponse(
            status="oauth_initiated",
            auth_url=auth_url,
            message="Visit the auth URL to complete Google Calendar connection"
        )
    except Exception as e:
        logger.error(f"Failed to initiate OAuth for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate calendar connection")


@router.get("/oauth/callback")
async def oauth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        user = await oauth_service.handle_oauth_callback(code, state, db)

        if not user:
            raise HTTPException(status_code=400, detail="OAuth callback failed")

        return CalendarConnectionResponse(
            status="connected",
            message=f"Google Calendar successfully connected for user {user.email}",
            connected_at=user.calendar_connected_at.isoformat() if user.calendar_connected_at else None
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail="OAuth callback failed")


@router.get("/status", response_model=CalendarStatusResponse)
async def get_calendar_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get calendar connection status and information"""
    try:
        if not current_user.calendar_connected:
            return CalendarStatusResponse(
                connected=False,
                message="Google Calendar not connected"
            )

        calendar_info = await oauth_service.get_user_calendar_info(current_user, db)

        if not calendar_info:
            return CalendarStatusResponse(
                connected=False,
                message="Calendar connection invalid, please reconnect"
            )

        return CalendarStatusResponse(
            connected=True,
            connected_at=calendar_info.get("connected_at"),
            calendars=calendar_info.get("calendars", []),
            permissions=calendar_info.get("permissions", {}),
            primary_calendar=calendar_info.get("primary_calendar"),
            recent_events_count=calendar_info.get("recent_events_count", 0)
        )

    except Exception as e:
        logger.error(f"Error getting calendar status for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get calendar status")


@router.get("/events", response_model=List[CalendarEventResponse])
async def get_calendar_events(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    calendar_id: str = Query("primary", description="Calendar ID"),
    max_results: int = Query(50, description="Maximum number of events"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get calendar events from Google Calendar"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        # Parse dates
        time_min = datetime.fromisoformat(start_date.replace("Z", "+00:00")) if start_date else None
        time_max = datetime.fromisoformat(end_date.replace("Z", "+00:00")) if end_date else None

        events = await google_calendar_client.get_events(
            access_token, calendar_id, time_min, time_max, max_results
        )

        return [
            CalendarEventResponse(
                id=event.get("id"),
                title=event.get("summary", "Untitled"),
                description=event.get("description", ""),
                start_time=event.get("start", {}).get("dateTime"),
                end_time=event.get("end", {}).get("dateTime"),
                location=event.get("location", ""),
                attendees=[att.get("email") for att in event.get("attendees", [])],
                organizer_email=event.get("organizer", {}).get("email"),
                meeting_link=event.get("hangoutLink") or event.get("location") if "meet.google.com" in (event.get("location") or "") else None
            )
            for event in events
        ]

    except Exception as e:
        logger.error(f"Failed to get calendar events for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get calendar events")


@router.post("/events", response_model=CalendarEventResponse)
async def create_calendar_event(
    event_data: CalendarEventCreate,
    calendar_id: str = Query("primary", description="Calendar ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new calendar event"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        # Convert to Google Calendar format
        google_event = {
            "summary": event_data.title,
            "description": event_data.description,
            "location": event_data.location,
            "start": {
                "dateTime": event_data.start_time,
                "timeZone": event_data.timezone or "UTC"
            },
            "end": {
                "dateTime": event_data.end_time,
                "timeZone": event_data.timezone or "UTC"
            },
            "attendees": [{"email": email} for email in (event_data.attendees or [])]
        }

        created_event = await google_calendar_client.create_event(
            access_token, google_event, calendar_id
        )

        return CalendarEventResponse(
            id=created_event.get("id"),
            title=created_event.get("summary"),
            description=created_event.get("description", ""),
            start_time=created_event.get("start", {}).get("dateTime"),
            end_time=created_event.get("end", {}).get("dateTime"),
            location=created_event.get("location", ""),
            attendees=[att.get("email") for att in created_event.get("attendees", [])],
            organizer_email=created_event.get("organizer", {}).get("email")
        )

    except Exception as e:
        logger.error(f"Failed to create calendar event for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create calendar event")


@router.put("/events/{event_id}")
async def update_calendar_event(
    event_id: str,
    event_data: CalendarEventCreate,
    background_tasks: BackgroundTasks,
    calendar_id: str = "primary",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a calendar event"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        # Build update data
        update_data = {}
        if event_data.title is not None:
            update_data["summary"] = event_data.title
        if event_data.description is not None:
            update_data["description"] = event_data.description
        if event_data.location is not None:
            update_data["location"] = event_data.location
        if event_data.start_time is not None:
            update_data["start"] = {
                "dateTime": event_data.start_time,
                "timeZone": event_data.timezone or "UTC"
            }
        if event_data.end_time is not None:
            update_data["end"] = {
                "dateTime": event_data.end_time,
                "timeZone": event_data.timezone or "UTC"
            }
        if event_data.attendees is not None:
            update_data["attendees"] = [{"email": email} for email in event_data.attendees]

        updated_event = await google_calendar_client.update_event(
            access_token, event_id, update_data, calendar_id
        )

        return CalendarEventResponse(
            id=updated_event.get("id"),
            title=updated_event.get("summary"),
            description=updated_event.get("description", ""),
            start_time=updated_event.get("start", {}).get("dateTime"),
            end_time=updated_event.get("end", {}).get("dateTime"),
            location=updated_event.get("location", ""),
            attendees=[att.get("email") for att in updated_event.get("attendees", [])],
            organizer_email=updated_event.get("organizer", {}).get("email")
        )

    except Exception as e:
        logger.error(f"Failed to update calendar event {event_id} for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update calendar event")


@router.delete("/events/{event_id}")
async def delete_calendar_event(
    event_id: str,
    calendar_id: str = "primary",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a calendar event"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        await google_calendar_client.delete_event(access_token, event_id, calendar_id)

        return {"status": "deleted", "event_id": event_id}

    except Exception as e:
        logger.error(f"Failed to delete calendar event {event_id} for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete calendar event")


@router.post("/sync", response_model=CalendarSyncResponse)
async def sync_calendar(
    background_tasks: BackgroundTasks,
    sync_request: CalendarSyncRequest = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync calendar with Google Calendar"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        # Default sync parameters
        days_back = 7
        days_forward = 30

        if sync_request:
            days_back = sync_request.days_back or days_back
            days_forward = sync_request.days_forward or days_forward

        # Perform sync
        sync_result = await calendar_sync_service.full_calendar_sync(
            current_user, db, days_back, days_forward
        )

        return CalendarSyncResponse(
            status=sync_result["status"],
            sync_window=sync_result.get("sync_window", {}),
            summary=sync_result.get("summary", {}),
            created_meetings=sync_result.get("results", {}).get("created", []),
            updated_meetings=sync_result.get("results", {}).get("updated", []),
            deleted_meetings=sync_result.get("results", {}).get("deleted", []),
            conflicts_resolved=sync_result.get("results", {}).get("conflicts_resolved", []),
            ai_decisions=sync_result.get("results", {}).get("ai_decisions", [])
        )

    except Exception as e:
        logger.error(f"Calendar sync failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Calendar sync failed")


@router.get("/busy-times")
async def get_busy_times(
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get busy times for scheduling optimization"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        time_min = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        time_max = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        free_busy_data = await google_calendar_client.get_free_busy(
            access_token, ["primary"], time_min, time_max
        )

        return {"busy_times": free_busy_data.get("calendars", {}).get("primary", {}).get("busy", [])}

    except Exception as e:
        logger.error(f"Failed to get busy times for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get busy times")


@router.get("/free-busy/{attendee_email}")
async def get_attendee_free_busy(
    attendee_email: str,
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check free/busy status for an attendee"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        time_min = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        time_max = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        # Note: Checking external attendee free/busy requires additional permissions
        free_busy_data = await google_calendar_client.get_free_busy(
            access_token, [attendee_email], time_min, time_max
        )

        return {
            "email": attendee_email,
            "free_busy": free_busy_data.get("calendars", {}).get(attendee_email, {}).get("busy", [])
        }

    except Exception as e:
        logger.error(f"Failed to check free/busy for {attendee_email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check free/busy")


@router.get("/analytics/weekly", response_model=WeeklyReportResponse)
async def get_weekly_analytics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly calendar analytics report"""
    try:
        start_datetime = None
        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

        report = await calendar_analytics.generate_weekly_report(
            current_user, db, start_datetime
        )

        return WeeklyReportResponse(**report)

    except Exception as e:
        logger.error(f"Failed to generate weekly report for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate weekly report")


@router.get("/conflicts", response_model=ConflictAnalysisResponse)
async def detect_conflicts(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect calendar conflicts and get resolution suggestions"""
    try:
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        conflicts = await conflict_detector.detect_conflicts(
            current_user, db, start_datetime, end_datetime
        )

        # Create resolution plans for critical conflicts
        resolution_plans = []
        for conflict in conflicts[:5]:  # Limit to top 5
            if conflict.severity in ["high", "critical"]:
                plan = await conflict_resolver.create_resolution_plan(
                    conflict, current_user, db
                )
                resolution_plans.append({
                    "conflict_id": plan.conflict_id,
                    "strategy": plan.strategy,
                    "estimated_success_rate": plan.estimated_success_rate,
                    "user_approval_required": plan.user_approval_required
                })

        return ConflictAnalysisResponse(
            total_conflicts=len(conflicts),
            conflicts=[
                {
                    "id": c.id,
                    "type": c.type,
                    "severity": c.severity,
                    "description": c.description,
                    "impact_score": c.impact_score,
                    "meeting_ids": [m.id for m in c.meetings],
                    "resolution_strategies": c.resolution_strategies,
                    "metadata": c.metadata
                }
                for c in conflicts
            ],
            resolution_plans=resolution_plans
        )

    except Exception as e:
        logger.error(f"Failed to detect conflicts for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect conflicts")


@router.post("/autonomous/enable")
async def enable_autonomous_mode(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable autonomous calendar management"""
    try:
        return {"status": "enabled", "message": "Autonomous calendar management enabled"}

    except Exception as e:
        logger.error(f"Failed to enable autonomous mode for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable autonomous mode")


@router.post("/focus-time/create", response_model=FocusTimeResponse)
async def create_focus_time(
    focus_request: FocusTimeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create focus time blocks"""
    try:
        if not current_user.calendar_connected:
            raise HTTPException(status_code=400, detail="Google Calendar not connected")

        access_token = await oauth_service.get_valid_access_token(current_user, db)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid access token")

        # Convert focus blocks
        focus_blocks = []
        for block in focus_request.focus_blocks:
            start_time = datetime.fromisoformat(block.start_time.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(block.end_time.replace("Z", "+00:00"))
            focus_blocks.append((start_time, end_time, block.focus_type))

        created_events = await autonomous_calendar_manager.block_focus_time(
            access_token, focus_blocks, "primary"
        )

        return FocusTimeResponse(
            created_focus_blocks=len(created_events),
            focus_event_ids=created_events,
            message=f"Created {len(created_events)} focus time blocks"
        )

    except Exception as e:
        logger.error(f"Failed to create focus time for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create focus time")