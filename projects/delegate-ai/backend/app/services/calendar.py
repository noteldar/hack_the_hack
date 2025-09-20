from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.meeting import Meeting


class CalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_calendar_events(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Meeting]:
        """Get calendar events/meetings for date range"""
        query = select(Meeting).where(Meeting.user_id == user_id)

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.where(Meeting.start_time >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(Meeting.end_time <= end_datetime)

        query = query.order_by(Meeting.start_time.asc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def check_availability(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if user is available during time slot"""
        query = select(Meeting).where(
            and_(
                Meeting.user_id == user_id,
                Meeting.start_time < end_time,
                Meeting.end_time > start_time
            )
        )

        result = await self.db.execute(query)
        conflicting_meetings = result.scalars().all()

        return len(conflicting_meetings) == 0

    async def find_available_slots(
        self,
        user_id: int,
        duration_minutes: int,
        start_date: date,
        end_date: date,
        working_hours_start: int = 9,
        working_hours_end: int = 17
    ) -> List[dict]:
        """Find available time slots for scheduling"""
        available_slots = []

        # Get all meetings in the date range
        meetings = await self.get_calendar_events(user_id, start_date, end_date)

        # Iterate through each day
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends (basic implementation)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                day_start = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=working_hours_start)
                )
                day_end = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=working_hours_end)
                )

                # Get meetings for this day
                day_meetings = [
                    m for m in meetings
                    if m.start_time.date() == current_date
                ]

                # Sort meetings by start time
                day_meetings.sort(key=lambda x: x.start_time)

                # Find gaps between meetings
                current_time = day_start
                for meeting in day_meetings:
                    # Check if there's a gap before this meeting
                    if meeting.start_time > current_time:
                        gap_duration = (meeting.start_time - current_time).total_seconds() / 60
                        if gap_duration >= duration_minutes:
                            available_slots.append({
                                "start_time": current_time,
                                "end_time": meeting.start_time,
                                "duration_minutes": int(gap_duration)
                            })

                    current_time = max(current_time, meeting.end_time)

                # Check if there's time after the last meeting
                if current_time < day_end:
                    gap_duration = (day_end - current_time).total_seconds() / 60
                    if gap_duration >= duration_minutes:
                        available_slots.append({
                            "start_time": current_time,
                            "end_time": day_end,
                            "duration_minutes": int(gap_duration)
                        })

                # If no meetings this day, the entire day is available
                if not day_meetings:
                    total_duration = (day_end - day_start).total_seconds() / 60
                    if total_duration >= duration_minutes:
                        available_slots.append({
                            "start_time": day_start,
                            "end_time": day_end,
                            "duration_minutes": int(total_duration)
                        })

            current_date += timedelta(days=1)

        return available_slots