"""
Google Calendar API integration service with OAuth 2.0 authentication
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.user import User
from app.models.meeting import Meeting
import logging

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """Google Calendar API client with OAuth 2.0 support"""

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/calendar.freebusy"
        ]
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"

    def get_auth_url(self, state: str = None) -> str:
        """Generate OAuth 2.0 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }

            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }

            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        json_data: Dict = None,
        params: Dict = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Google Calendar API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

    async def get_calendars(self, access_token: str) -> List[Dict[str, Any]]:
        """Get user's calendar list"""
        response = await self._make_authenticated_request(
            "GET", "/users/me/calendarList", access_token
        )
        return response.get("items", [])

    async def get_events(
        self,
        access_token: str,
        calendar_id: str = "primary",
        time_min: datetime = None,
        time_max: datetime = None,
        max_results: int = 2500
    ) -> List[Dict[str, Any]]:
        """Get calendar events within time range"""
        params = {
            "maxResults": max_results,
            "orderBy": "startTime",
            "singleEvents": True
        }

        if time_min:
            params["timeMin"] = time_min.isoformat()
        if time_max:
            params["timeMax"] = time_max.isoformat()

        response = await self._make_authenticated_request(
            "GET", f"/calendars/{calendar_id}/events", access_token, params=params
        )
        return response.get("items", [])

    async def create_event(
        self,
        access_token: str,
        event_data: Dict[str, Any],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Create a new calendar event"""
        return await self._make_authenticated_request(
            "POST", f"/calendars/{calendar_id}/events", access_token, json_data=event_data
        )

    async def update_event(
        self,
        access_token: str,
        event_id: str,
        event_data: Dict[str, Any],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Update an existing calendar event"""
        return await self._make_authenticated_request(
            "PUT", f"/calendars/{calendar_id}/events/{event_id}", access_token, json_data=event_data
        )

    async def delete_event(
        self,
        access_token: str,
        event_id: str,
        calendar_id: str = "primary"
    ) -> None:
        """Delete a calendar event"""
        await self._make_authenticated_request(
            "DELETE", f"/calendars/{calendar_id}/events/{event_id}", access_token
        )

    async def get_free_busy(
        self,
        access_token: str,
        calendar_ids: List[str],
        time_min: datetime,
        time_max: datetime
    ) -> Dict[str, Any]:
        """Get free/busy information for calendars"""
        data = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "items": [{"id": cal_id} for cal_id in calendar_ids]
        }

        return await self._make_authenticated_request(
            "POST", "/freebusy", access_token, json_data=data
        )

    async def respond_to_event(
        self,
        access_token: str,
        event_id: str,
        response_status: str,  # "accepted", "declined", "tentative"
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Respond to a calendar event invitation"""
        # First get the event to update attendee status
        event = await self._make_authenticated_request(
            "GET", f"/calendars/{calendar_id}/events/{event_id}", access_token
        )

        # Update attendee response
        attendees = event.get("attendees", [])
        user_email = await self._get_user_email(access_token)

        for attendee in attendees:
            if attendee.get("email") == user_email:
                attendee["responseStatus"] = response_status
                break

        event_data = {"attendees": attendees}
        return await self.update_event(access_token, event_id, event_data, calendar_id)

    async def _get_user_email(self, access_token: str) -> str:
        """Get the authenticated user's email"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers=headers
            )
            response.raise_for_status()
            return response.json().get("email")


class AutonomousCalendarManager:
    """Autonomous calendar management with AI decision making"""

    def __init__(self, calendar_client: GoogleCalendarClient):
        self.calendar_client = calendar_client

    async def auto_decline_meeting(
        self,
        access_token: str,
        event_id: str,
        reason: str = None,
        calendar_id: str = "primary"
    ) -> bool:
        """Automatically decline a meeting with AI-generated response"""
        try:
            # Generate decline message
            decline_message = self._generate_decline_message(reason)

            # Get the event first
            event = await self.calendar_client._make_authenticated_request(
                "GET", f"/calendars/{calendar_id}/events/{event_id}", access_token
            )

            # Update event with decline and message
            attendees = event.get("attendees", [])
            user_email = await self.calendar_client._get_user_email(access_token)

            for attendee in attendees:
                if attendee.get("email") == user_email:
                    attendee["responseStatus"] = "declined"
                    attendee["comment"] = decline_message
                    break

            event_data = {"attendees": attendees}
            await self.calendar_client.update_event(access_token, event_id, event_data, calendar_id)

            logger.info(f"Auto-declined meeting {event_id}: {reason}")
            return True

        except Exception as e:
            logger.error(f"Failed to auto-decline meeting {event_id}: {e}")
            return False

    async def reschedule_meeting(
        self,
        access_token: str,
        event_id: str,
        new_start_time: datetime,
        new_end_time: datetime,
        calendar_id: str = "primary"
    ) -> bool:
        """Reschedule a meeting to optimize calendar"""
        try:
            event_data = {
                "start": {
                    "dateTime": new_start_time.isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": new_end_time.isoformat(),
                    "timeZone": "UTC"
                }
            }

            await self.calendar_client.update_event(access_token, event_id, event_data, calendar_id)
            logger.info(f"Rescheduled meeting {event_id} to {new_start_time}")
            return True

        except Exception as e:
            logger.error(f"Failed to reschedule meeting {event_id}: {e}")
            return False

    async def create_buffer_time(
        self,
        access_token: str,
        before_event_id: str = None,
        after_event_id: str = None,
        buffer_minutes: int = 15,
        calendar_id: str = "primary"
    ) -> List[str]:
        """Create buffer time around meetings"""
        created_events = []

        try:
            if before_event_id:
                # Get the event to create buffer before
                event = await self.calendar_client._make_authenticated_request(
                    "GET", f"/calendars/{calendar_id}/events/{before_event_id}", access_token
                )

                event_start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                buffer_start = event_start - timedelta(minutes=buffer_minutes)

                buffer_event = {
                    "summary": "🛡️ Buffer Time",
                    "description": "Automatically created buffer time for meeting preparation",
                    "start": {
                        "dateTime": buffer_start.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": event_start.isoformat(),
                        "timeZone": "UTC"
                    },
                    "transparency": "transparent"  # Show as free time
                }

                result = await self.calendar_client.create_event(access_token, buffer_event, calendar_id)
                created_events.append(result["id"])

            if after_event_id:
                # Get the event to create buffer after
                event = await self.calendar_client._make_authenticated_request(
                    "GET", f"/calendars/{calendar_id}/events/{after_event_id}", access_token
                )

                event_end = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
                buffer_end = event_end + timedelta(minutes=buffer_minutes)

                buffer_event = {
                    "summary": "🧠 Decompression Buffer",
                    "description": "Automatically created buffer time for meeting recovery",
                    "start": {
                        "dateTime": event_end.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": buffer_end.isoformat(),
                        "timeZone": "UTC"
                    },
                    "transparency": "transparent"
                }

                result = await self.calendar_client.create_event(access_token, buffer_event, calendar_id)
                created_events.append(result["id"])

        except Exception as e:
            logger.error(f"Failed to create buffer time: {e}")

        return created_events

    async def block_focus_time(
        self,
        access_token: str,
        focus_blocks: List[Tuple[datetime, datetime, str]] = None,
        calendar_id: str = "primary"
    ) -> List[str]:
        """Automatically block focus time slots"""
        if not focus_blocks:
            # Default focus time blocks (9-11 AM, 2-4 PM daily for next week)
            focus_blocks = self._get_default_focus_blocks()

        created_events = []

        for start_time, end_time, focus_type in focus_blocks:
            try:
                # Check if time slot is available
                busy_times = await self.calendar_client.get_free_busy(
                    access_token, [calendar_id], start_time, end_time
                )

                if not self._is_time_slot_free(busy_times, calendar_id, start_time, end_time):
                    continue

                focus_event = {
                    "summary": f"🎯 Deep Focus Time - {focus_type}",
                    "description": "Automatically blocked focus time for deep work",
                    "start": {
                        "dateTime": start_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": end_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "reminders": {
                        "useDefault": False,
                        "overrides": [
                            {"method": "popup", "minutes": 5}
                        ]
                    }
                }

                result = await self.calendar_client.create_event(access_token, focus_event, calendar_id)
                created_events.append(result["id"])

            except Exception as e:
                logger.error(f"Failed to create focus time block: {e}")

        return created_events

    def _generate_decline_message(self, reason: str = None) -> str:
        """Generate professional decline message"""
        base_messages = [
            "Thank you for the invitation. Unfortunately, I won't be able to attend due to scheduling conflicts.",
            "I appreciate being included, but I have a prior commitment during this time.",
            "Thanks for thinking of me for this meeting. I won't be able to join due to calendar conflicts.",
        ]

        if reason:
            return f"{base_messages[0]} {reason}"

        return base_messages[0]

    def _get_default_focus_blocks(self) -> List[Tuple[datetime, datetime, str]]:
        """Get default focus time blocks for the next week"""
        blocks = []
        now = datetime.now(timezone.utc)

        for day in range(7):  # Next 7 days
            date = now + timedelta(days=day)

            # Skip weekends
            if date.weekday() >= 5:
                continue

            # Morning focus block (9-11 AM)
            morning_start = date.replace(hour=9, minute=0, second=0, microsecond=0)
            morning_end = date.replace(hour=11, minute=0, second=0, microsecond=0)
            blocks.append((morning_start, morning_end, "Deep Work"))

            # Afternoon focus block (2-4 PM)
            afternoon_start = date.replace(hour=14, minute=0, second=0, microsecond=0)
            afternoon_end = date.replace(hour=16, minute=0, second=0, microsecond=0)
            blocks.append((afternoon_start, afternoon_end, "Creative Work"))

        return blocks

    def _is_time_slot_free(
        self,
        free_busy_response: Dict[str, Any],
        calendar_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if a time slot is free based on free/busy response"""
        calendars = free_busy_response.get("calendars", {})
        calendar_info = calendars.get(calendar_id, {})
        busy_periods = calendar_info.get("busy", [])

        for busy_period in busy_periods:
            busy_start = datetime.fromisoformat(busy_period["start"].replace("Z", "+00:00"))
            busy_end = datetime.fromisoformat(busy_period["end"].replace("Z", "+00:00"))

            # Check for overlap
            if start_time < busy_end and end_time > busy_start:
                return False

        return True


# Global instances
google_calendar_client = GoogleCalendarClient()
autonomous_calendar_manager = AutonomousCalendarManager(google_calendar_client)