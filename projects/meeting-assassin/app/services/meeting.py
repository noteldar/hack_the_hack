"""
Meeting management service
"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta

from app.models.meeting import Meeting


class MeetingService:
    """Service for meeting management and analysis"""

    async def detect_conflicts(self, user_id: int, days_ahead: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts for upcoming meetings"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)

        # Get all meetings for the period
        query = select(Meeting).where(
            and_(
                Meeting.user_id == user_id,
                Meeting.start_time >= datetime.utcnow(),
                Meeting.start_time <= end_date
            )
        ).order_by(Meeting.start_time)

        result = await db.execute(query)
        meetings = result.scalars().all()

        conflicts = []

        # Check for overlapping meetings
        for i, meeting1 in enumerate(meetings):
            for meeting2 in meetings[i+1:]:
                if (meeting1.start_time < meeting2.end_time and
                    meeting1.end_time > meeting2.start_time):

                    conflicts.append({
                        "conflict_id": f"{meeting1.id}_{meeting2.id}",
                        "meetings": [
                            {
                                "id": meeting1.id,
                                "title": meeting1.title,
                                "start_time": meeting1.start_time.isoformat(),
                                "end_time": meeting1.end_time.isoformat(),
                                "priority": meeting1.priority
                            },
                            {
                                "id": meeting2.id,
                                "title": meeting2.title,
                                "start_time": meeting2.start_time.isoformat(),
                                "end_time": meeting2.end_time.isoformat(),
                                "priority": meeting2.priority
                            }
                        ],
                        "overlap_minutes": self._calculate_overlap_minutes(meeting1, meeting2),
                        "severity": self._calculate_conflict_severity(meeting1, meeting2)
                    })

        return conflicts

    def _calculate_overlap_minutes(self, meeting1: Meeting, meeting2: Meeting) -> int:
        """Calculate overlap duration between two meetings"""
        overlap_start = max(meeting1.start_time, meeting2.start_time)
        overlap_end = min(meeting1.end_time, meeting2.end_time)

        if overlap_start < overlap_end:
            return int((overlap_end - overlap_start).total_seconds() / 60)
        return 0

    def _calculate_conflict_severity(self, meeting1: Meeting, meeting2: Meeting) -> str:
        """Calculate conflict severity based on priorities and overlap"""
        overlap_minutes = self._calculate_overlap_minutes(meeting1, meeting2)

        if overlap_minutes >= 45:
            return "high"
        elif overlap_minutes >= 15:
            return "medium"
        else:
            return "low"