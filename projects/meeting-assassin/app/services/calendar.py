"""
Google Calendar integration service
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.user import User
from app.schemas.calendar import CalendarEventCreate


class CalendarService:
    """Service for Google Calendar integration"""

    def __init__(self):
        pass

    def _get_calendar_service(self, user: User):
        """Get Google Calendar service instance"""
        credentials = Credentials(token=user.access_token)
        return build('calendar', 'v3', credentials=credentials)

    async def get_user_calendars(self, user: User) -> List[Dict[str, Any]]:
        """Get user's Google calendars"""
        service = self._get_calendar_service(user)
        calendar_list = service.calendarList().list().execute()
        return calendar_list.get('items', [])

    async def get_events(self, user: User, calendar_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get calendar events for date range"""
        service = self._get_calendar_service(user)

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    async def create_event(self, user: User, calendar_id: str, event_data: CalendarEventCreate) -> Dict[str, Any]:
        """Create a new calendar event"""
        service = self._get_calendar_service(user)

        event = {
            'summary': event_data.summary,
            'description': event_data.description,
            'location': event_data.location,
            'start': {
                'dateTime': event_data.start,
                'timeZone': user.timezone,
            },
            'end': {
                'dateTime': event_data.end,
                'timeZone': user.timezone,
            },
            'attendees': [{'email': email} for email in (event_data.attendees or [])]
        }

        return service.events().insert(calendarId=calendar_id, body=event).execute()

    async def update_event(self, user: User, calendar_id: str, event_id: str, event_data: CalendarEventCreate) -> Dict[str, Any]:
        """Update an existing calendar event"""
        service = self._get_calendar_service(user)

        event = {
            'summary': event_data.summary,
            'description': event_data.description,
            'location': event_data.location,
            'start': {
                'dateTime': event_data.start,
                'timeZone': user.timezone,
            },
            'end': {
                'dateTime': event_data.end,
                'timeZone': user.timezone,
            },
            'attendees': [{'email': email} for email in (event_data.attendees or [])]
        }

        return service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

    async def delete_event(self, user: User, calendar_id: str, event_id: str):
        """Delete a calendar event"""
        service = self._get_calendar_service(user)
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    async def get_busy_times(self, user: User, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get busy times for scheduling optimization"""
        service = self._get_calendar_service(user)

        body = {
            "timeMin": start_date,
            "timeMax": end_date,
            "items": [{"id": "primary"}]
        }

        result = service.freebusy().query(body=body).execute()
        return result.get('calendars', {}).get('primary', {}).get('busy', [])

    async def get_attendee_free_busy(self, user: User, attendee_email: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Check free/busy status for an attendee"""
        service = self._get_calendar_service(user)

        body = {
            "timeMin": start_date,
            "timeMax": end_date,
            "items": [{"id": attendee_email}]
        }

        result = service.freebusy().query(body=body).execute()
        return result.get('calendars', {}).get(attendee_email, {}).get('busy', [])

    async def quick_add_event(self, user: User, text: str) -> Dict[str, Any]:
        """Quick add event using natural language"""
        service = self._get_calendar_service(user)
        return service.events().quickAdd(calendarId='primary', text=text).execute()

    async def full_calendar_sync(self, user_id: int, days_ahead: int):
        """Full calendar synchronization (placeholder)"""
        # Implementation would sync all events with database
        pass

    async def analyze_quick_added_event(self, event_id: str, user_id: int):
        """Analyze quick-added event (placeholder)"""
        # Implementation would analyze the event and store in database
        pass