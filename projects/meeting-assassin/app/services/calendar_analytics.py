"""
Calendar analytics and reporting service for productivity insights
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus, AIDecisionType
from app.services.google_calendar import google_calendar_client
from app.services.oauth_service import oauth_service
import logging
import statistics

logger = logging.getLogger(__name__)


class CalendarAnalytics:
    """Advanced calendar analytics and productivity insights"""

    def __init__(self):
        self.calendar_client = google_calendar_client
        self.oauth_service = oauth_service

    async def generate_weekly_report(
        self,
        user: User,
        db: AsyncSession,
        start_date: datetime = None
    ) -> Dict[str, Any]:
        """Generate comprehensive weekly calendar report"""

        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=7)

        end_date = start_date + timedelta(days=7)

        # Get meetings for the week
        meetings = await self._get_meetings_for_period(user, db, start_date, end_date)

        # Basic metrics
        total_meetings = len(meetings)
        total_hours = sum((m.end_time - m.start_time).total_seconds() / 3600 for m in meetings)

        # Meeting patterns
        daily_breakdown = await self._analyze_daily_patterns(meetings)
        hourly_distribution = await self._analyze_hourly_distribution(meetings)
        meeting_types = await self._analyze_meeting_types(meetings)

        # AI decision analysis
        ai_decisions = await self._analyze_ai_decisions(meetings)

        # Productivity metrics
        productivity_metrics = await self._calculate_productivity_metrics(meetings, user, db)

        # Focus time analysis
        focus_time_analysis = await self._analyze_focus_time(meetings, start_date, end_date)

        # Conflict analysis
        conflict_analysis = await self._analyze_conflicts(meetings)

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": 7
            },
            "summary": {
                "total_meetings": total_meetings,
                "total_hours": round(total_hours, 2),
                "average_meetings_per_day": round(total_meetings / 7, 1),
                "average_hours_per_day": round(total_hours / 7, 2),
                "average_meeting_duration": round(total_hours * 60 / total_meetings, 1) if total_meetings > 0 else 0
            },
            "patterns": {
                "daily_breakdown": daily_breakdown,
                "hourly_distribution": hourly_distribution,
                "meeting_types": meeting_types
            },
            "ai_insights": {
                "decisions": ai_decisions,
                "productivity_metrics": productivity_metrics,
                "focus_time": focus_time_analysis,
                "conflicts": conflict_analysis
            },
            "recommendations": await self._generate_recommendations(meetings, user, db)
        }

    async def generate_monthly_report(
        self,
        user: User,
        db: AsyncSession,
        month: int = None,
        year: int = None
    ) -> Dict[str, Any]:
        """Generate comprehensive monthly calendar report"""

        now = datetime.now(timezone.utc)
        if not month:
            month = now.month
        if not year:
            year = now.year

        # Calculate month boundaries
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        # Get meetings for the month
        meetings = await self._get_meetings_for_period(user, db, start_date, end_date)

        # Weekly breakdown
        weekly_stats = []
        current_week_start = start_date
        while current_week_start < end_date:
            current_week_end = min(current_week_start + timedelta(days=7), end_date)
            week_meetings = [
                m for m in meetings
                if current_week_start <= m.start_time < current_week_end
            ]

            weekly_stats.append({
                "week_start": current_week_start.isoformat(),
                "meeting_count": len(week_meetings),
                "total_hours": sum((m.end_time - m.start_time).total_seconds() / 3600 for m in week_meetings),
                "ai_declined": len([m for m in week_meetings if m.ai_decision == AIDecisionType.AUTO_DECLINE])
            })
            current_week_start = current_week_end

        # Month trends
        trends = await self._analyze_monthly_trends(meetings)

        return {
            "period": {
                "month": month,
                "year": year,
                "month_name": start_date.strftime("%B"),
                "total_days": (end_date - start_date).days
            },
            "summary": {
                "total_meetings": len(meetings),
                "total_hours": round(sum((m.end_time - m.start_time).total_seconds() / 3600 for m in meetings), 2),
                "busiest_day": await self._find_busiest_day(meetings),
                "quietest_day": await self._find_quietest_day(meetings)
            },
            "weekly_breakdown": weekly_stats,
            "trends": trends,
            "efficiency": await self._calculate_monthly_efficiency(meetings, user, db)
        }

    async def track_meeting_patterns(
        self,
        user: User,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Track meeting patterns and identify trends"""

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        meetings = await self._get_meetings_for_period(user, db, start_date, end_date)

        patterns = {
            "recurring_meetings": await self._identify_recurring_meetings(meetings),
            "meeting_initiators": await self._analyze_meeting_initiators(meetings),
            "common_attendees": await self._analyze_common_attendees(meetings),
            "location_patterns": await self._analyze_location_patterns(meetings),
            "duration_patterns": await self._analyze_duration_patterns(meetings)
        }

        return patterns

    async def predict_scheduling_conflicts(
        self,
        user: User,
        db: AsyncSession,
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        """Predict potential scheduling conflicts"""

        now = datetime.now(timezone.utc)
        future_date = now + timedelta(days=days_ahead)

        # Get current meetings in the prediction window
        meetings = await self._get_meetings_for_period(user, db, now, future_date)

        conflicts = []

        # Check for back-to-back meetings without buffer
        for i, meeting1 in enumerate(meetings):
            for meeting2 in meetings[i + 1:]:
                time_gap = abs((meeting1.end_time - meeting2.start_time).total_seconds() / 60)

                if time_gap < 15:  # Less than 15 minutes between meetings
                    conflicts.append({
                        "type": "insufficient_buffer",
                        "severity": "medium",
                        "meeting1": {
                            "id": meeting1.id,
                            "title": meeting1.title,
                            "end_time": meeting1.end_time.isoformat()
                        },
                        "meeting2": {
                            "id": meeting2.id,
                            "title": meeting2.title,
                            "start_time": meeting2.start_time.isoformat()
                        },
                        "gap_minutes": int(time_gap),
                        "recommendation": "Add buffer time or reschedule one meeting"
                    })

        # Check for overloaded days
        daily_meetings = defaultdict(list)
        for meeting in meetings:
            daily_meetings[meeting.start_time.date()].append(meeting)

        for date, day_meetings in daily_meetings.items():
            if len(day_meetings) > 6:  # More than 6 meetings in a day
                total_hours = sum((m.end_time - m.start_time).total_seconds() / 3600 for m in day_meetings)

                conflicts.append({
                    "type": "overloaded_day",
                    "severity": "high",
                    "date": date.isoformat(),
                    "meeting_count": len(day_meetings),
                    "total_hours": round(total_hours, 2),
                    "recommendation": "Consider rescheduling some meetings to distribute load"
                })

        return conflicts

    async def _get_meetings_for_period(
        self,
        user: User,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[Meeting]:
        """Get meetings for a specific time period"""
        result = await db.execute(
            select(Meeting).where(
                and_(
                    Meeting.user_id == user.id,
                    Meeting.start_time >= start_date,
                    Meeting.start_time < end_date
                )
            ).order_by(Meeting.start_time)
        )
        return result.scalars().all()

    async def _analyze_daily_patterns(self, meetings: List[Meeting]) -> Dict[str, Any]:
        """Analyze daily meeting patterns"""
        daily_counts = Counter()
        daily_hours = defaultdict(float)

        for meeting in meetings:
            day_name = meeting.start_time.strftime("%A")
            duration_hours = (meeting.end_time - meeting.start_time).total_seconds() / 3600

            daily_counts[day_name] += 1
            daily_hours[day_name] += duration_hours

        return {
            "meeting_counts": dict(daily_counts),
            "meeting_hours": {day: round(hours, 2) for day, hours in daily_hours.items()},
            "busiest_day": max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None,
            "lightest_day": min(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None
        }

    async def _analyze_hourly_distribution(self, meetings: List[Meeting]) -> Dict[int, int]:
        """Analyze meeting distribution by hour"""
        hourly_counts = Counter()

        for meeting in meetings:
            hourly_counts[meeting.start_time.hour] += 1

        return dict(hourly_counts)

    async def _analyze_meeting_types(self, meetings: List[Meeting]) -> Dict[str, Any]:
        """Analyze meeting types and patterns"""
        type_counts = Counter()
        type_durations = defaultdict(list)

        for meeting in meetings:
            meeting_type = meeting.meeting_type or "general"
            duration_minutes = (meeting.end_time - meeting.start_time).total_seconds() / 60

            type_counts[meeting_type] += 1
            type_durations[meeting_type].append(duration_minutes)

        return {
            "counts": dict(type_counts),
            "average_durations": {
                mtype: round(statistics.mean(durations), 1)
                for mtype, durations in type_durations.items()
            }
        }

    async def _analyze_ai_decisions(self, meetings: List[Meeting]) -> Dict[str, Any]:
        """Analyze AI decision patterns"""
        decision_counts = Counter()
        decision_confidence = defaultdict(list)

        for meeting in meetings:
            if meeting.ai_decision:
                decision_counts[meeting.ai_decision] += 1
                if meeting.ai_decision_confidence:
                    decision_confidence[meeting.ai_decision].append(meeting.ai_decision_confidence)

        avg_confidence = {
            decision: round(statistics.mean(confidences), 2)
            for decision, confidences in decision_confidence.items()
        }

        return {
            "decision_counts": dict(decision_counts),
            "average_confidence": avg_confidence,
            "total_automated_decisions": sum(decision_counts.values())
        }

    async def _calculate_productivity_metrics(
        self,
        meetings: List[Meeting],
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate productivity metrics"""
        if not meetings:
            return {}

        # Meetings with productivity scores
        scored_meetings = [m for m in meetings if m.productivity_score is not None]

        if not scored_meetings:
            return {"message": "No productivity scores available"}

        avg_productivity = statistics.mean([m.productivity_score for m in scored_meetings])

        # High productivity meetings (score > 0.7)
        high_productivity = [m for m in scored_meetings if m.productivity_score > 0.7]

        # Low productivity meetings (score < 0.3)
        low_productivity = [m for m in scored_meetings if m.productivity_score < 0.3]

        return {
            "average_productivity_score": round(avg_productivity, 2),
            "high_productivity_meetings": len(high_productivity),
            "low_productivity_meetings": len(low_productivity),
            "productivity_trend": "improving" if avg_productivity > 0.6 else "needs_attention"
        }

    async def _analyze_focus_time(
        self,
        meetings: List[Meeting],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze focus time availability"""

        # Define focus time blocks (9-11 AM, 2-4 PM)
        focus_blocks = []
        current_date = start_date.date()

        while current_date < end_date.date():
            # Skip weekends
            if current_date.weekday() < 5:
                # Morning focus block
                morning_start = datetime.combine(current_date, datetime.min.time().replace(hour=9))
                morning_end = datetime.combine(current_date, datetime.min.time().replace(hour=11))
                focus_blocks.append(("morning", morning_start, morning_end))

                # Afternoon focus block
                afternoon_start = datetime.combine(current_date, datetime.min.time().replace(hour=14))
                afternoon_end = datetime.combine(current_date, datetime.min.time().replace(hour=16))
                focus_blocks.append(("afternoon", afternoon_start, afternoon_end))

            current_date += timedelta(days=1)

        # Check which focus blocks are interrupted by meetings
        interrupted_blocks = 0
        available_focus_hours = 0

        for block_type, block_start, block_end in focus_blocks:
            block_interrupted = False
            for meeting in meetings:
                # Check if meeting overlaps with focus block
                if (meeting.start_time < block_end and meeting.end_time > block_start):
                    block_interrupted = True
                    break

            if block_interrupted:
                interrupted_blocks += 1
            else:
                available_focus_hours += 2  # Each block is 2 hours

        total_focus_blocks = len(focus_blocks)
        focus_utilization = (interrupted_blocks / total_focus_blocks * 100) if total_focus_blocks > 0 else 0

        return {
            "total_focus_blocks": total_focus_blocks,
            "interrupted_blocks": interrupted_blocks,
            "available_blocks": total_focus_blocks - interrupted_blocks,
            "available_focus_hours": available_focus_hours,
            "focus_utilization_percent": round(focus_utilization, 1),
            "recommendation": "Good focus time protection" if focus_utilization < 50 else "Consider protecting more focus time"
        }

    async def _analyze_conflicts(self, meetings: List[Meeting]) -> Dict[str, Any]:
        """Analyze meeting conflicts and overlaps"""
        conflicts = []
        back_to_back_count = 0

        for i, meeting1 in enumerate(meetings):
            for meeting2 in meetings[i + 1:]:
                # Check for direct overlap
                if (meeting1.start_time < meeting2.end_time and meeting1.end_time > meeting2.start_time):
                    conflicts.append({
                        "meeting1_title": meeting1.title,
                        "meeting2_title": meeting2.title,
                        "overlap_minutes": int((
                            min(meeting1.end_time, meeting2.end_time) -
                            max(meeting1.start_time, meeting2.start_time)
                        ).total_seconds() / 60)
                    })

                # Check for back-to-back meetings (less than 15 minutes gap)
                time_gap = abs((meeting1.end_time - meeting2.start_time).total_seconds() / 60)
                if 0 <= time_gap <= 15:
                    back_to_back_count += 1

        return {
            "direct_conflicts": len(conflicts),
            "conflict_details": conflicts[:5],  # Show first 5 conflicts
            "back_to_back_meetings": back_to_back_count,
            "conflict_score": min(len(conflicts) / len(meetings) if meetings else 0, 1.0)
        }

    async def _generate_recommendations(
        self,
        meetings: List[Meeting],
        user: User,
        db: AsyncSession
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if not meetings:
            return ["No meetings found for analysis period"]

        # Meeting load recommendations
        daily_meetings = defaultdict(list)
        for meeting in meetings:
            daily_meetings[meeting.start_time.date()].append(meeting)

        overloaded_days = [date for date, day_meetings in daily_meetings.items() if len(day_meetings) > 6]
        if overloaded_days:
            recommendations.append(
                f"You have {len(overloaded_days)} overloaded days with 6+ meetings. "
                "Consider rescheduling some meetings to distribute the load."
            )

        # Focus time recommendations
        focus_conflicts = len([
            m for m in meetings
            if (9 <= m.start_time.hour <= 11) or (14 <= m.start_time.hour <= 16)
        ])

        if focus_conflicts > len(meetings) * 0.3:
            recommendations.append(
                "30%+ of your meetings conflict with focus time blocks (9-11 AM, 2-4 PM). "
                "Consider protecting these times for deep work."
            )

        # Meeting duration recommendations
        long_meetings = [m for m in meetings if (m.end_time - m.start_time).total_seconds() / 3600 > 1.5]
        if len(long_meetings) > len(meetings) * 0.2:
            recommendations.append(
                "You have many long meetings (>1.5 hours). Consider breaking them into shorter sessions."
            )

        # AI decision recommendations
        declined_meetings = len([m for m in meetings if m.ai_decision == AIDecisionType.AUTO_DECLINE])
        if declined_meetings > 0:
            recommendations.append(
                f"AI auto-declined {declined_meetings} meetings this period. "
                "Review decline reasons to optimize your calendar further."
            )

        return recommendations[:5]  # Return top 5 recommendations

    async def _analyze_monthly_trends(self, meetings: List[Meeting]) -> Dict[str, Any]:
        """Analyze trends over the month"""
        if not meetings:
            return {}

        # Group meetings by week
        weekly_data = defaultdict(list)
        for meeting in meetings:
            week_number = meeting.start_time.isocalendar()[1]
            weekly_data[week_number].append(meeting)

        # Calculate trends
        weekly_counts = [len(week_meetings) for week_meetings in weekly_data.values()]
        weekly_hours = [
            sum((m.end_time - m.start_time).total_seconds() / 3600 for m in week_meetings)
            for week_meetings in weekly_data.values()
        ]

        trend_direction = "stable"
        if len(weekly_counts) >= 2:
            if weekly_counts[-1] > weekly_counts[0]:
                trend_direction = "increasing"
            elif weekly_counts[-1] < weekly_counts[0]:
                trend_direction = "decreasing"

        return {
            "meeting_count_trend": trend_direction,
            "weekly_meeting_counts": weekly_counts,
            "weekly_hours": [round(h, 2) for h in weekly_hours],
            "peak_week": weekly_counts.index(max(weekly_counts)) + 1 if weekly_counts else None
        }

    async def _find_busiest_day(self, meetings: List[Meeting]) -> Optional[Dict[str, Any]]:
        """Find the busiest day in the period"""
        daily_counts = defaultdict(int)
        daily_hours = defaultdict(float)

        for meeting in meetings:
            date = meeting.start_time.date()
            duration_hours = (meeting.end_time - meeting.start_time).total_seconds() / 3600

            daily_counts[date] += 1
            daily_hours[date] += duration_hours

        if not daily_counts:
            return None

        busiest_date = max(daily_counts.items(), key=lambda x: x[1])

        return {
            "date": busiest_date[0].isoformat(),
            "meeting_count": busiest_date[1],
            "total_hours": round(daily_hours[busiest_date[0]], 2)
        }

    async def _find_quietest_day(self, meetings: List[Meeting]) -> Optional[Dict[str, Any]]:
        """Find the quietest day in the period"""
        daily_counts = defaultdict(int)
        daily_hours = defaultdict(float)

        for meeting in meetings:
            date = meeting.start_time.date()
            duration_hours = (meeting.end_time - meeting.start_time).total_seconds() / 3600

            daily_counts[date] += 1
            daily_hours[date] += duration_hours

        if not daily_counts:
            return None

        quietest_date = min(daily_counts.items(), key=lambda x: x[1])

        return {
            "date": quietest_date[0].isoformat(),
            "meeting_count": quietest_date[1],
            "total_hours": round(daily_hours[quietest_date[0]], 2)
        }

    async def _calculate_monthly_efficiency(
        self,
        meetings: List[Meeting],
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate monthly calendar efficiency metrics"""
        if not meetings:
            return {}

        total_meetings = len(meetings)
        total_hours = sum((m.end_time - m.start_time).total_seconds() / 3600 for m in meetings)

        # AI optimization metrics
        ai_optimized = len([m for m in meetings if m.ai_decision])
        auto_declined = len([m for m in meetings if m.ai_decision == AIDecisionType.AUTO_DECLINE])
        rescheduled = len([m for m in meetings if m.ai_decision == AIDecisionType.SUGGEST_RESCHEDULE])

        # Time saved through AI decisions (estimated)
        time_saved_hours = auto_declined * 1.0 + rescheduled * 0.5  # Rough estimates

        return {
            "total_meetings": total_meetings,
            "total_hours": round(total_hours, 2),
            "ai_optimization_rate": round((ai_optimized / total_meetings) * 100, 1) if total_meetings > 0 else 0,
            "auto_declined_meetings": auto_declined,
            "rescheduled_suggestions": rescheduled,
            "estimated_time_saved_hours": round(time_saved_hours, 2),
            "efficiency_score": round(min((time_saved_hours / total_hours) * 100, 100), 1) if total_hours > 0 else 0
        }

    async def _identify_recurring_meetings(self, meetings: List[Meeting]) -> List[Dict[str, Any]]:
        """Identify recurring meeting patterns"""
        # Group meetings by title similarity
        title_groups = defaultdict(list)

        for meeting in meetings:
            # Simple title matching (could be more sophisticated)
            clean_title = meeting.title.lower().strip()
            title_groups[clean_title].append(meeting)

        # Find groups with multiple meetings (potential recurring meetings)
        recurring = []
        for title, meeting_list in title_groups.items():
            if len(meeting_list) >= 2:  # At least 2 instances
                # Calculate average interval
                if len(meeting_list) > 1:
                    intervals = []
                    sorted_meetings = sorted(meeting_list, key=lambda m: m.start_time)
                    for i in range(1, len(sorted_meetings)):
                        interval_days = (sorted_meetings[i].start_time.date() -
                                       sorted_meetings[i-1].start_time.date()).days
                        intervals.append(interval_days)

                    avg_interval = statistics.mean(intervals) if intervals else 0

                    recurring.append({
                        "title": title,
                        "instance_count": len(meeting_list),
                        "average_interval_days": round(avg_interval, 1),
                        "likely_recurring": avg_interval in [1, 7, 14, 30]  # Daily, weekly, bi-weekly, monthly
                    })

        return recurring[:10]  # Return top 10

    async def _analyze_meeting_initiators(self, meetings: List[Meeting]) -> Dict[str, int]:
        """Analyze who initiates meetings most often"""
        initiator_counts = Counter()

        for meeting in meetings:
            if meeting.organizer_email:
                initiator_counts[meeting.organizer_email] += 1

        return dict(initiator_counts.most_common(10))

    async def _analyze_common_attendees(self, meetings: List[Meeting]) -> Dict[str, int]:
        """Analyze most common meeting attendees"""
        attendee_counts = Counter()

        for meeting in meetings:
            if meeting.attendees:
                for attendee in meeting.attendees:
                    if isinstance(attendee, dict) and "email" in attendee:
                        attendee_counts[attendee["email"]] += 1
                    elif isinstance(attendee, str):
                        attendee_counts[attendee] += 1

        return dict(attendee_counts.most_common(10))

    async def _analyze_location_patterns(self, meetings: List[Meeting]) -> Dict[str, int]:
        """Analyze meeting location patterns"""
        location_counts = Counter()

        for meeting in meetings:
            if meeting.location:
                # Clean and normalize location
                location = meeting.location.strip().lower()
                if "zoom" in location or "teams" in location or "meet" in location:
                    location_counts["virtual"] += 1
                elif location:
                    location_counts[location] += 1
            else:
                location_counts["no_location"] += 1

        return dict(location_counts.most_common(10))

    async def _analyze_duration_patterns(self, meetings: List[Meeting]) -> Dict[str, Any]:
        """Analyze meeting duration patterns"""
        durations_minutes = [
            (meeting.end_time - meeting.start_time).total_seconds() / 60
            for meeting in meetings
        ]

        if not durations_minutes:
            return {}

        # Common duration buckets
        duration_buckets = {
            "15min": len([d for d in durations_minutes if d <= 15]),
            "30min": len([d for d in durations_minutes if 15 < d <= 30]),
            "1hour": len([d for d in durations_minutes if 30 < d <= 60]),
            "1-2hours": len([d for d in durations_minutes if 60 < d <= 120]),
            "2hours+": len([d for d in durations_minutes if d > 120])
        }

        return {
            "duration_distribution": duration_buckets,
            "average_duration_minutes": round(statistics.mean(durations_minutes), 1),
            "median_duration_minutes": round(statistics.median(durations_minutes), 1),
            "most_common_duration": max(duration_buckets.items(), key=lambda x: x[1])[0]
        }


# Global instance
calendar_analytics = CalendarAnalytics()