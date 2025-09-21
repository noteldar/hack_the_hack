"""
Real-time calendar synchronization service with conflict detection and resolution
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus, AIDecisionType
from app.services.google_calendar import google_calendar_client
from app.services.oauth_service import oauth_service
from app.services.meeting_intelligence import meeting_intelligence_service
from app.core.websocket import websocket_manager
import logging

logger = logging.getLogger(__name__)


class CalendarSyncService:
    """Real-time calendar synchronization with Google Calendar"""

    def __init__(self):
        self.calendar_client = google_calendar_client
        self.oauth_service = oauth_service
        self.intelligence_service = meeting_intelligence_service
        self.sync_locks = {}  # User-specific sync locks to prevent concurrent syncs

    async def full_calendar_sync(
        self,
        user: User,
        db: AsyncSession,
        days_back: int = 7,
        days_forward: int = 30
    ) -> Dict[str, Any]:
        """Perform full calendar synchronization"""

        # Prevent concurrent syncs for the same user
        if user.id in self.sync_locks:
            return {"status": "sync_in_progress", "message": "Sync already running for user"}

        self.sync_locks[user.id] = True

        try:
            access_token = await self.oauth_service.get_valid_access_token(user, db)
            if not access_token:
                return {"status": "error", "message": "No valid access token"}

            # Define sync window
            now = datetime.now(timezone.utc)
            start_time = now - timedelta(days=days_back)
            end_time = now + timedelta(days=days_forward)

            # Get Google Calendar events
            try:
                google_events = await self.calendar_client.get_events(
                    access_token,
                    "primary",
                    start_time,
                    end_time,
                    max_results=500
                )
            except Exception as e:
                logger.error(f"Error fetching Google Calendar events for user {user.id}: {e}")
                return {"status": "error", "message": f"Failed to fetch calendar events: {str(e)}"}

            # Get existing meetings from database
            existing_meetings = await self._get_existing_meetings(user, db, start_time, end_time)

            # Sync results
            sync_results = {
                "created": [],
                "updated": [],
                "deleted": [],
                "conflicts_resolved": [],
                "ai_decisions": []
            }

            # Create lookup for existing meetings by Google event ID
            existing_by_google_id = {m.google_event_id: m for m in existing_meetings if m.google_event_id}

            # Process Google Calendar events
            processed_google_ids = set()

            for google_event in google_events:
                google_event_id = google_event.get("id")
                if not google_event_id:
                    continue

                processed_google_ids.add(google_event_id)

                if google_event_id in existing_by_google_id:
                    # Update existing meeting
                    meeting = existing_by_google_id[google_event_id]
                    updated = await self._update_meeting_from_google_event(
                        meeting, google_event, user, db
                    )
                    if updated:
                        sync_results["updated"].append({
                            "id": meeting.id,
                            "title": meeting.title,
                            "changes": updated
                        })
                else:
                    # Create new meeting
                    meeting = await self._create_meeting_from_google_event(
                        google_event, user, db
                    )
                    if meeting:
                        sync_results["created"].append({
                            "id": meeting.id,
                            "title": meeting.title,
                            "google_event_id": meeting.google_event_id
                        })

                        # Run AI analysis for new meetings
                        try:
                            ai_analysis = await self.intelligence_service.analyze_meeting(
                                google_event, user, db
                            )

                            # Update meeting with AI analysis
                            meeting.ai_importance_score = ai_analysis.get("importance_score")
                            meeting.ai_conflict_score = ai_analysis.get("conflict_score")
                            meeting.ai_productivity_impact = ai_analysis.get("productivity_impact")

                            ai_decision = ai_analysis.get("ai_decision", {})
                            meeting.ai_decision = ai_decision.get("type")
                            meeting.ai_decision_confidence = ai_decision.get("confidence")
                            meeting.ai_decision_reasoning = ai_decision.get("reasoning")

                            await db.commit()

                            # Execute autonomous actions if configured
                            if user.autonomous_mode:  # Assume user has this setting
                                actions_result = await self.intelligence_service.execute_autonomous_actions(
                                    user, google_event, ai_decision, db
                                )
                                if actions_result["success"]:
                                    sync_results["ai_decisions"].append({
                                        "meeting_id": meeting.id,
                                        "decision": ai_decision.get("type"),
                                        "actions": actions_result["executed_actions"]
                                    })

                        except Exception as e:
                            logger.error(f"AI analysis failed for meeting {meeting.id}: {e}")

            # Handle deleted meetings (exist in DB but not in Google Calendar)
            for meeting in existing_meetings:
                if meeting.google_event_id and meeting.google_event_id not in processed_google_ids:
                    # Meeting was deleted from Google Calendar
                    meeting.status = MeetingStatus.CANCELLED
                    sync_results["deleted"].append({
                        "id": meeting.id,
                        "title": meeting.title,
                        "reason": "deleted_from_google_calendar"
                    })

            # Detect and resolve conflicts
            conflicts = await self._detect_conflicts(user, db, start_time, end_time)
            for conflict in conflicts:
                resolution = await self._resolve_conflict(conflict, user, db)
                if resolution:
                    sync_results["conflicts_resolved"].append(resolution)

            await db.commit()

            # Notify frontend via WebSocket
            await self._notify_sync_completion(user.id, sync_results)

            return {
                "status": "success",
                "sync_window": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "results": sync_results,
                "summary": {
                    "total_google_events": len(google_events),
                    "created_meetings": len(sync_results["created"]),
                    "updated_meetings": len(sync_results["updated"]),
                    "deleted_meetings": len(sync_results["deleted"]),
                    "conflicts_resolved": len(sync_results["conflicts_resolved"]),
                    "ai_decisions_executed": len(sync_results["ai_decisions"])
                }
            }

        except Exception as e:
            logger.error(f"Full calendar sync failed for user {user.id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            # Release sync lock
            self.sync_locks.pop(user.id, None)

    async def incremental_sync(
        self,
        user: User,
        db: AsyncSession,
        since: datetime = None
    ) -> Dict[str, Any]:
        """Perform incremental calendar synchronization"""

        if not since:
            since = datetime.now(timezone.utc) - timedelta(hours=1)

        access_token = await self.oauth_service.get_valid_access_token(user, db)
        if not access_token:
            return {"status": "error", "message": "No valid access token"}

        # For incremental sync, we'll check the last hour of events
        # In a production system, you'd use Google Calendar's push notifications
        # or sync tokens for more efficient incremental sync

        end_time = datetime.now(timezone.utc) + timedelta(days=1)

        try:
            # Get recent events
            recent_events = await self.calendar_client.get_events(
                access_token,
                "primary",
                since,
                end_time,
                max_results=50
            )

            sync_results = {"updated": [], "created": [], "ai_decisions": []}

            for google_event in recent_events:
                google_event_id = google_event.get("id")
                if not google_event_id:
                    continue

                # Check if meeting exists
                result = await db.execute(
                    select(Meeting).where(
                        and_(
                            Meeting.user_id == user.id,
                            Meeting.google_event_id == google_event_id
                        )
                    )
                )
                existing_meeting = result.scalar_one_or_none()

                if existing_meeting:
                    # Update existing
                    updated = await self._update_meeting_from_google_event(
                        existing_meeting, google_event, user, db
                    )
                    if updated:
                        sync_results["updated"].append({
                            "id": existing_meeting.id,
                            "title": existing_meeting.title
                        })
                else:
                    # Create new
                    new_meeting = await self._create_meeting_from_google_event(
                        google_event, user, db
                    )
                    if new_meeting:
                        sync_results["created"].append({
                            "id": new_meeting.id,
                            "title": new_meeting.title
                        })

            await db.commit()
            return {"status": "success", "results": sync_results}

        except Exception as e:
            logger.error(f"Incremental sync failed for user {user.id}: {e}")
            return {"status": "error", "message": str(e)}

    async def sync_meeting_to_google(
        self,
        meeting: Meeting,
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Sync a database meeting to Google Calendar"""

        access_token = await self.oauth_service.get_valid_access_token(user, db)
        if not access_token:
            return {"status": "error", "message": "No valid access token"}

        try:
            event_data = meeting.to_calendar_event()

            if meeting.google_event_id:
                # Update existing event
                updated_event = await self.calendar_client.update_event(
                    access_token,
                    meeting.google_event_id,
                    event_data,
                    meeting.calendar_id or "primary"
                )
                return {"status": "updated", "google_event_id": updated_event["id"]}
            else:
                # Create new event
                created_event = await self.calendar_client.create_event(
                    access_token,
                    event_data,
                    meeting.calendar_id or "primary"
                )
                meeting.google_event_id = created_event["id"]
                await db.commit()
                return {"status": "created", "google_event_id": created_event["id"]}

        except Exception as e:
            logger.error(f"Failed to sync meeting {meeting.id} to Google: {e}")
            return {"status": "error", "message": str(e)}

    async def _get_existing_meetings(
        self,
        user: User,
        db: AsyncSession,
        start_time: datetime,
        end_time: datetime
    ) -> List[Meeting]:
        """Get existing meetings from database for sync period"""
        result = await db.execute(
            select(Meeting).where(
                and_(
                    Meeting.user_id == user.id,
                    or_(
                        and_(Meeting.start_time >= start_time, Meeting.start_time <= end_time),
                        and_(Meeting.end_time >= start_time, Meeting.end_time <= end_time),
                        and_(Meeting.start_time <= start_time, Meeting.end_time >= end_time)
                    )
                )
            )
        )
        return result.scalars().all()

    async def _create_meeting_from_google_event(
        self,
        google_event: Dict[str, Any],
        user: User,
        db: AsyncSession
    ) -> Optional[Meeting]:
        """Create a new meeting from Google Calendar event"""

        try:
            # Parse event data
            start_data = google_event.get("start", {})
            end_data = google_event.get("end", {})

            # Handle different datetime formats
            if "dateTime" in start_data:
                start_time = datetime.fromisoformat(start_data["dateTime"].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(end_data["dateTime"].replace("Z", "+00:00"))
            elif "date" in start_data:
                # All-day event
                start_date = datetime.strptime(start_data["date"], "%Y-%m-%d").date()
                end_date = datetime.strptime(end_data["date"], "%Y-%m-%d").date()
                start_time = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                end_time = datetime.combine(end_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            else:
                logger.error(f"Invalid datetime format in Google event: {google_event}")
                return None

            # Extract attendees
            attendees = []
            if "attendees" in google_event:
                attendees = [
                    attendee.get("email", "")
                    for attendee in google_event["attendees"]
                    if attendee.get("email")
                ]

            # Calculate duration
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

            # Create meeting
            meeting = Meeting(
                user_id=user.id,
                google_event_id=google_event.get("id"),
                calendar_id=google_event.get("organizer", {}).get("email", "primary"),
                title=google_event.get("summary", "Untitled Meeting"),
                description=google_event.get("description", ""),
                location=google_event.get("location", ""),
                start_time=start_time,
                end_time=end_time,
                timezone=start_data.get("timeZone", "UTC"),
                duration_minutes=duration_minutes,
                organizer_email=google_event.get("organizer", {}).get("email"),
                attendees=attendees,
                status=MeetingStatus.SCHEDULED,
                meeting_link=self._extract_meeting_link(google_event),
                last_ai_analysis=datetime.utcnow()
            )

            db.add(meeting)
            await db.flush()  # Get the meeting ID

            return meeting

        except Exception as e:
            logger.error(f"Error creating meeting from Google event: {e}")
            return None

    async def _update_meeting_from_google_event(
        self,
        meeting: Meeting,
        google_event: Dict[str, Any],
        user: User,
        db: AsyncSession
    ) -> List[str]:
        """Update existing meeting from Google Calendar event"""

        changes = []

        try:
            # Check for changes
            new_title = google_event.get("summary", "Untitled Meeting")
            if meeting.title != new_title:
                meeting.title = new_title
                changes.append("title")

            new_description = google_event.get("description", "")
            if meeting.description != new_description:
                meeting.description = new_description
                changes.append("description")

            new_location = google_event.get("location", "")
            if meeting.location != new_location:
                meeting.location = new_location
                changes.append("location")

            # Check time changes
            start_data = google_event.get("start", {})
            end_data = google_event.get("end", {})

            if "dateTime" in start_data:
                new_start_time = datetime.fromisoformat(start_data["dateTime"].replace("Z", "+00:00"))
                new_end_time = datetime.fromisoformat(end_data["dateTime"].replace("Z", "+00:00"))

                if meeting.start_time != new_start_time:
                    meeting.start_time = new_start_time
                    changes.append("start_time")

                if meeting.end_time != new_end_time:
                    meeting.end_time = new_end_time
                    changes.append("end_time")

                # Update duration
                new_duration = int((new_end_time - new_start_time).total_seconds() / 60)
                if meeting.duration_minutes != new_duration:
                    meeting.duration_minutes = new_duration
                    changes.append("duration")

            # Check attendees
            new_attendees = []
            if "attendees" in google_event:
                new_attendees = [
                    attendee.get("email", "")
                    for attendee in google_event["attendees"]
                    if attendee.get("email")
                ]

            if set(meeting.attendees or []) != set(new_attendees):
                meeting.attendees = new_attendees
                changes.append("attendees")

            # Update meeting link
            new_meeting_link = self._extract_meeting_link(google_event)
            if meeting.meeting_link != new_meeting_link:
                meeting.meeting_link = new_meeting_link
                changes.append("meeting_link")

            if changes:
                meeting.updated_at = datetime.utcnow()

            return changes

        except Exception as e:
            logger.error(f"Error updating meeting {meeting.id} from Google event: {e}")
            return []

    def _extract_meeting_link(self, google_event: Dict[str, Any]) -> Optional[str]:
        """Extract video meeting link from Google Calendar event"""

        # Check in conferenceData
        conference_data = google_event.get("conferenceData", {})
        if conference_data:
            entry_points = conference_data.get("entryPoints", [])
            for entry_point in entry_points:
                if entry_point.get("entryPointType") == "video":
                    return entry_point.get("uri")

        # Check in description
        description = google_event.get("description", "")
        if description:
            # Look for common video meeting patterns
            import re
            patterns = [
                r"https://[a-zA-Z0-9.-]+\.zoom\.us/j/[0-9]+",
                r"https://meet\.google\.com/[a-zA-Z0-9-]+",
                r"https://teams\.microsoft\.com/l/meetup-join/[a-zA-Z0-9%_.-]+",
                r"https://[a-zA-Z0-9.-]+\.webex\.com/[a-zA-Z0-9/.-]+",
            ]

            for pattern in patterns:
                match = re.search(pattern, description)
                if match:
                    return match.group(0)

        # Check in location
        location = google_event.get("location", "")
        if location and ("zoom.us" in location or "meet.google.com" in location or "teams.microsoft.com" in location):
            return location

        return None

    async def _detect_conflicts(
        self,
        user: User,
        db: AsyncSession,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Detect calendar conflicts"""

        # Get all meetings in the time range
        result = await db.execute(
            select(Meeting).where(
                and_(
                    Meeting.user_id == user.id,
                    Meeting.start_time >= start_time,
                    Meeting.end_time <= end_time,
                    Meeting.status == MeetingStatus.SCHEDULED
                )
            ).order_by(Meeting.start_time)
        )
        meetings = result.scalars().all()

        conflicts = []

        # Check for overlapping meetings
        for i, meeting1 in enumerate(meetings):
            for meeting2 in meetings[i + 1:]:
                # Check for time overlap
                if (meeting1.start_time < meeting2.end_time and
                    meeting1.end_time > meeting2.start_time):

                    overlap_start = max(meeting1.start_time, meeting2.start_time)
                    overlap_end = min(meeting1.end_time, meeting2.end_time)
                    overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60

                    conflicts.append({
                        "type": "time_overlap",
                        "severity": "high" if overlap_minutes > 15 else "medium",
                        "meeting1": {
                            "id": meeting1.id,
                            "title": meeting1.title,
                            "start_time": meeting1.start_time,
                            "end_time": meeting1.end_time
                        },
                        "meeting2": {
                            "id": meeting2.id,
                            "title": meeting2.title,
                            "start_time": meeting2.start_time,
                            "end_time": meeting2.end_time
                        },
                        "overlap_minutes": int(overlap_minutes)
                    })

        # Check for insufficient buffer time
        for i in range(len(meetings) - 1):
            current_meeting = meetings[i]
            next_meeting = meetings[i + 1]

            gap_minutes = (next_meeting.start_time - current_meeting.end_time).total_seconds() / 60

            if 0 <= gap_minutes < 15:  # Less than 15 minutes between meetings
                conflicts.append({
                    "type": "insufficient_buffer",
                    "severity": "low" if gap_minutes >= 5 else "medium",
                    "meeting1": {
                        "id": current_meeting.id,
                        "title": current_meeting.title,
                        "end_time": current_meeting.end_time
                    },
                    "meeting2": {
                        "id": next_meeting.id,
                        "title": next_meeting.title,
                        "start_time": next_meeting.start_time
                    },
                    "gap_minutes": int(gap_minutes)
                })

        return conflicts

    async def _resolve_conflict(
        self,
        conflict: Dict[str, Any],
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Attempt to resolve a calendar conflict"""

        conflict_type = conflict["type"]
        severity = conflict["severity"]

        if conflict_type == "time_overlap" and severity == "high":
            # For high-severity overlaps, suggest rescheduling the lower-priority meeting
            meeting1_id = conflict["meeting1"]["id"]
            meeting2_id = conflict["meeting2"]["id"]

            # Get the meetings
            meeting1_result = await db.execute(select(Meeting).where(Meeting.id == meeting1_id))
            meeting2_result = await db.execute(select(Meeting).where(Meeting.id == meeting2_id))

            meeting1 = meeting1_result.scalar_one_or_none()
            meeting2 = meeting2_result.scalar_one_or_none()

            if not meeting1 or not meeting2:
                return None

            # Determine which meeting to reschedule based on AI importance scores
            target_meeting = meeting1 if (meeting1.ai_importance_score or 0.5) < (meeting2.ai_importance_score or 0.5) else meeting2

            # Mark for rescheduling
            target_meeting.ai_decision = AIDecisionType.SUGGEST_RESCHEDULE
            target_meeting.ai_decision_reasoning = f"Conflicts with higher-priority meeting: {conflict['overlap_minutes']} minutes overlap"

            return {
                "conflict_id": f"{meeting1_id}_{meeting2_id}",
                "resolution": "suggest_reschedule",
                "target_meeting_id": target_meeting.id,
                "reason": target_meeting.ai_decision_reasoning
            }

        elif conflict_type == "insufficient_buffer":
            # For insufficient buffer, create buffer time if possible
            try:
                access_token = await self.oauth_service.get_valid_access_token(user, db)
                if access_token:
                    from app.services.google_calendar import autonomous_calendar_manager

                    buffer_events = await autonomous_calendar_manager.create_buffer_time(
                        access_token,
                        before_event_id=conflict["meeting2"]["id"],
                        buffer_minutes=15 - int(conflict["gap_minutes"]),
                        calendar_id="primary"
                    )

                    if buffer_events:
                        return {
                            "conflict_id": f"{conflict['meeting1']['id']}_{conflict['meeting2']['id']}",
                            "resolution": "buffer_created",
                            "buffer_event_ids": buffer_events
                        }
            except Exception as e:
                logger.error(f"Failed to create buffer time: {e}")

        return None

    async def _notify_sync_completion(self, user_id: int, sync_results: Dict[str, Any]):
        """Notify frontend about sync completion via WebSocket"""
        try:
            message = {
                "type": "calendar_sync_complete",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "results": sync_results
            }

            await websocket_manager.send_personal_message(user_id, json.dumps(message))

        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {e}")

    async def schedule_automatic_sync(self, user: User, db: AsyncSession):
        """Schedule automatic periodic sync for user"""
        # This would typically be handled by a background task scheduler
        # For now, we'll just perform an incremental sync

        try:
            result = await self.incremental_sync(user, db)
            logger.info(f"Automatic sync completed for user {user.id}: {result['status']}")
        except Exception as e:
            logger.error(f"Automatic sync failed for user {user.id}: {e}")


# Global instance
calendar_sync_service = CalendarSyncService()