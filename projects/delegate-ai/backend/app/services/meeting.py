from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status

from app.models.meeting import Meeting, MeetingStatus
from app.schemas.meeting import MeetingCreate, MeetingUpdate


class MeetingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_meeting(self, user_id: int, meeting_create: MeetingCreate) -> Meeting:
        """Create a new meeting"""
        meeting = Meeting(
            title=meeting_create.title,
            description=meeting_create.description,
            start_time=meeting_create.start_time,
            end_time=meeting_create.end_time,
            timezone=meeting_create.timezone,
            location=meeting_create.location,
            meeting_url=meeting_create.meeting_url,
            is_recurring=meeting_create.is_recurring,
            recurrence_pattern=meeting_create.recurrence_pattern,
            agenda=meeting_create.agenda,
            attendees=meeting_create.attendees,
            calendar_event_id=meeting_create.calendar_event_id,
            calendar_provider=meeting_create.calendar_provider,
            user_id=user_id,
            status=MeetingStatus.SCHEDULED
        )

        self.db.add(meeting)
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def get_meeting_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID"""
        result = await self.db.execute(select(Meeting).where(Meeting.id == meeting_id))
        return result.scalar_one_or_none()

    async def get_user_meetings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[MeetingStatus] = None
    ) -> List[Meeting]:
        """Get user's meetings with filtering"""
        query = select(Meeting).where(Meeting.user_id == user_id)

        if status:
            query = query.where(Meeting.status == status)

        query = query.offset(skip).limit(limit).order_by(Meeting.start_time.asc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_meeting(self, meeting_id: int, meeting_update: MeetingUpdate) -> Meeting:
        """Update a meeting"""
        # Get existing meeting
        result = await self.db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = result.scalar_one_or_none()

        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )

        # Update fields
        update_data = meeting_update.model_dump(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(Meeting)
                .where(Meeting.id == meeting_id)
                .values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(meeting)

        return meeting

    async def delete_meeting(self, meeting_id: int) -> None:
        """Delete a meeting"""
        await self.db.execute(delete(Meeting).where(Meeting.id == meeting_id))
        await self.db.commit()