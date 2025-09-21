"""
Advanced conflict detection and resolution algorithms for calendar optimization
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus, MeetingPriority, AIDecisionType
from app.services.google_calendar import google_calendar_client, autonomous_calendar_manager
from app.services.oauth_service import oauth_service
from app.algorithms.genetic import genetic_scheduler
import logging

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Types of calendar conflicts"""
    DIRECT_OVERLAP = "direct_overlap"
    INSUFFICIENT_BUFFER = "insufficient_buffer"
    FOCUS_TIME_CONFLICT = "focus_time_conflict"
    COMMUTE_TIME_CONFLICT = "commute_time_conflict"
    OVERLOADED_DAY = "overloaded_day"
    DOUBLE_BOOKING = "double_booking"
    PREPARATION_TIME_CONFLICT = "preparation_time_conflict"
    LUNCH_CONFLICT = "lunch_conflict"
    TIMEZONE_CONFLICT = "timezone_conflict"


class ConflictSeverity(str, Enum):
    """Conflict severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStrategy(str, Enum):
    """Conflict resolution strategies"""
    AUTO_RESCHEDULE = "auto_reschedule"
    SUGGEST_ALTERNATIVE = "suggest_alternative"
    AUTO_DECLINE = "auto_decline"
    CREATE_BUFFER = "create_buffer"
    SPLIT_MEETING = "split_meeting"
    DELEGATE_MEETING = "delegate_meeting"
    REQUEST_CLARIFICATION = "request_clarification"
    OPTIMIZE_SCHEDULE = "optimize_schedule"


@dataclass
class Conflict:
    """Represents a calendar conflict"""
    id: str
    type: ConflictType
    severity: ConflictSeverity
    meetings: List[Meeting]
    description: str
    impact_score: float  # 0.0 to 1.0
    resolution_strategies: List[ResolutionStrategy]
    metadata: Dict[str, Any]


@dataclass
class ResolutionPlan:
    """Represents a conflict resolution plan"""
    conflict_id: str
    strategy: ResolutionStrategy
    actions: List[Dict[str, Any]]
    estimated_success_rate: float
    estimated_impact: float
    required_permissions: List[str]
    user_approval_required: bool


class ConflictDetector:
    """Advanced conflict detection system"""

    def __init__(self):
        self.conflict_rules = self._initialize_conflict_rules()

    def _initialize_conflict_rules(self) -> Dict[ConflictType, Dict[str, Any]]:
        """Initialize conflict detection rules"""
        return {
            ConflictType.DIRECT_OVERLAP: {
                "min_overlap_minutes": 1,
                "severity_thresholds": {
                    5: ConflictSeverity.LOW,
                    15: ConflictSeverity.MEDIUM,
                    30: ConflictSeverity.HIGH,
                    60: ConflictSeverity.CRITICAL
                }
            },
            ConflictType.INSUFFICIENT_BUFFER: {
                "min_buffer_minutes": 15,
                "severity_thresholds": {
                    5: ConflictSeverity.HIGH,
                    10: ConflictSeverity.MEDIUM,
                    15: ConflictSeverity.LOW
                }
            },
            ConflictType.FOCUS_TIME_CONFLICT: {
                "focus_blocks": [(9, 11), (14, 16)],  # 9-11 AM, 2-4 PM
                "importance_threshold": 0.7
            },
            ConflictType.OVERLOADED_DAY: {
                "max_meetings_per_day": 6,
                "max_hours_per_day": 8,
                "severity_multiplier": 1.2
            }
        }

    async def detect_conflicts(
        self,
        user: User,
        db: AsyncSession,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Conflict]:
        """Detect all types of conflicts in user's calendar"""

        if not start_date:
            start_date = datetime.now(timezone.utc)
        if not end_date:
            end_date = start_date + timedelta(days=14)

        # Get meetings in the time range
        meetings = await self._get_meetings_for_analysis(user, db, start_date, end_date)

        conflicts = []

        # Run all conflict detection algorithms
        conflicts.extend(await self._detect_direct_overlaps(meetings))
        conflicts.extend(await self._detect_insufficient_buffers(meetings))
        conflicts.extend(await self._detect_focus_time_conflicts(meetings, user))
        conflicts.extend(await self._detect_overloaded_days(meetings))
        conflicts.extend(await self._detect_preparation_conflicts(meetings))
        conflicts.extend(await self._detect_commute_conflicts(meetings))
        conflicts.extend(await self._detect_lunch_conflicts(meetings))
        conflicts.extend(await self._detect_timezone_conflicts(meetings))

        # Sort conflicts by severity and impact
        conflicts.sort(key=lambda c: (c.severity.value, -c.impact_score))

        return conflicts

    async def _get_meetings_for_analysis(
        self,
        user: User,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[Meeting]:
        """Get meetings for conflict analysis"""
        result = await db.execute(
            select(Meeting).where(
                and_(
                    Meeting.user_id == user.id,
                    Meeting.start_time >= start_date,
                    Meeting.start_time <= end_date,
                    Meeting.status == MeetingStatus.SCHEDULED
                )
            ).order_by(Meeting.start_time)
        )
        return result.scalars().all()

    async def _detect_direct_overlaps(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect meetings with direct time overlaps"""
        conflicts = []

        for i, meeting1 in enumerate(meetings):
            for meeting2 in meetings[i + 1:]:
                if self._meetings_overlap(meeting1, meeting2):
                    overlap_minutes = self._calculate_overlap_minutes(meeting1, meeting2)

                    severity = self._determine_overlap_severity(overlap_minutes)

                    conflicts.append(Conflict(
                        id=f"overlap_{meeting1.id}_{meeting2.id}",
                        type=ConflictType.DIRECT_OVERLAP,
                        severity=severity,
                        meetings=[meeting1, meeting2],
                        description=f"Meetings overlap by {overlap_minutes} minutes",
                        impact_score=min(overlap_minutes / 60, 1.0),
                        resolution_strategies=[
                            ResolutionStrategy.AUTO_RESCHEDULE,
                            ResolutionStrategy.AUTO_DECLINE,
                            ResolutionStrategy.SUGGEST_ALTERNATIVE
                        ],
                        metadata={
                            "overlap_minutes": overlap_minutes,
                            "overlap_start": max(meeting1.start_time, meeting2.start_time).isoformat(),
                            "overlap_end": min(meeting1.end_time, meeting2.end_time).isoformat()
                        }
                    ))

        return conflicts

    async def _detect_insufficient_buffers(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect meetings with insufficient buffer time"""
        conflicts = []
        min_buffer = self.conflict_rules[ConflictType.INSUFFICIENT_BUFFER]["min_buffer_minutes"]

        for i in range(len(meetings) - 1):
            current = meetings[i]
            next_meeting = meetings[i + 1]

            gap_minutes = (next_meeting.start_time - current.end_time).total_seconds() / 60

            if 0 <= gap_minutes < min_buffer:
                severity = self._determine_buffer_severity(gap_minutes)

                conflicts.append(Conflict(
                    id=f"buffer_{current.id}_{next_meeting.id}",
                    type=ConflictType.INSUFFICIENT_BUFFER,
                    severity=severity,
                    meetings=[current, next_meeting],
                    description=f"Only {int(gap_minutes)} minutes between meetings (need {min_buffer})",
                    impact_score=max(0.1, (min_buffer - gap_minutes) / min_buffer),
                    resolution_strategies=[
                        ResolutionStrategy.CREATE_BUFFER,
                        ResolutionStrategy.AUTO_RESCHEDULE,
                        ResolutionStrategy.SUGGEST_ALTERNATIVE
                    ],
                    metadata={
                        "gap_minutes": gap_minutes,
                        "required_buffer": min_buffer,
                        "buffer_deficit": min_buffer - gap_minutes
                    }
                ))

        return conflicts

    async def _detect_focus_time_conflicts(self, meetings: List[Meeting], user: User) -> List[Conflict]:
        """Detect meetings that conflict with focus time"""
        conflicts = []
        focus_blocks = self.conflict_rules[ConflictType.FOCUS_TIME_CONFLICT]["focus_blocks"]

        for meeting in meetings:
            hour = meeting.start_time.hour

            for focus_start, focus_end in focus_blocks:
                if focus_start <= hour < focus_end:
                    # Meeting conflicts with focus time
                    importance = meeting.ai_importance_score or 0.5

                    # Only flag as conflict if meeting importance is below threshold
                    if importance < self.conflict_rules[ConflictType.FOCUS_TIME_CONFLICT]["importance_threshold"]:
                        conflicts.append(Conflict(
                            id=f"focus_{meeting.id}",
                            type=ConflictType.FOCUS_TIME_CONFLICT,
                            severity=ConflictSeverity.MEDIUM if importance < 0.3 else ConflictSeverity.LOW,
                            meetings=[meeting],
                            description=f"Low-importance meeting during focus time ({focus_start}-{focus_end})",
                            impact_score=0.8 - importance,
                            resolution_strategies=[
                                ResolutionStrategy.AUTO_RESCHEDULE,
                                ResolutionStrategy.AUTO_DECLINE,
                                ResolutionStrategy.SUGGEST_ALTERNATIVE
                            ],
                            metadata={
                                "focus_block": f"{focus_start:02d}-{focus_end:02d}",
                                "meeting_importance": importance,
                                "meeting_hour": hour
                            }
                        ))
                    break

        return conflicts

    async def _detect_overloaded_days(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect days with too many meetings"""
        conflicts = []
        rules = self.conflict_rules[ConflictType.OVERLOADED_DAY]

        # Group meetings by day
        daily_meetings = {}
        for meeting in meetings:
            date = meeting.start_time.date()
            if date not in daily_meetings:
                daily_meetings[date] = []
            daily_meetings[date].append(meeting)

        for date, day_meetings in daily_meetings.items():
            meeting_count = len(day_meetings)
            total_hours = sum(
                (m.end_time - m.start_time).total_seconds() / 3600
                for m in day_meetings
            )

            if meeting_count > rules["max_meetings_per_day"] or total_hours > rules["max_hours_per_day"]:
                severity = ConflictSeverity.HIGH if meeting_count > 8 or total_hours > 10 else ConflictSeverity.MEDIUM

                conflicts.append(Conflict(
                    id=f"overload_{date.isoformat()}",
                    type=ConflictType.OVERLOADED_DAY,
                    severity=severity,
                    meetings=day_meetings,
                    description=f"Overloaded day: {meeting_count} meetings, {total_hours:.1f} hours",
                    impact_score=min((meeting_count / rules["max_meetings_per_day"]) * rules["severity_multiplier"], 1.0),
                    resolution_strategies=[
                        ResolutionStrategy.AUTO_RESCHEDULE,
                        ResolutionStrategy.OPTIMIZE_SCHEDULE,
                        ResolutionStrategy.DELEGATE_MEETING
                    ],
                    metadata={
                        "date": date.isoformat(),
                        "meeting_count": meeting_count,
                        "total_hours": total_hours,
                        "max_allowed_meetings": rules["max_meetings_per_day"],
                        "max_allowed_hours": rules["max_hours_per_day"]
                    }
                ))

        return conflicts

    async def _detect_preparation_conflicts(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect meetings that need preparation time but don't have it"""
        conflicts = []

        high_prep_keywords = ["presentation", "demo", "pitch", "interview", "review"]

        for i, meeting in enumerate(meetings):
            # Determine if meeting needs preparation
            needs_prep = any(keyword in meeting.title.lower() for keyword in high_prep_keywords)

            if needs_prep:
                required_prep = 30  # 30 minutes preparation time

                # Check if there's enough time before the meeting
                if i > 0:
                    prev_meeting = meetings[i - 1]
                    available_prep = (meeting.start_time - prev_meeting.end_time).total_seconds() / 60
                else:
                    # First meeting of the day, check if it's early enough
                    meeting_hour = meeting.start_time.hour
                    available_prep = (meeting_hour - 9) * 60 if meeting_hour >= 9 else 0

                if available_prep < required_prep:
                    conflicts.append(Conflict(
                        id=f"prep_{meeting.id}",
                        type=ConflictType.PREPARATION_TIME_CONFLICT,
                        severity=ConflictSeverity.MEDIUM,
                        meetings=[meeting],
                        description=f"Insufficient preparation time: need {required_prep}min, have {int(available_prep)}min",
                        impact_score=(required_prep - available_prep) / required_prep,
                        resolution_strategies=[
                            ResolutionStrategy.CREATE_BUFFER,
                            ResolutionStrategy.AUTO_RESCHEDULE,
                            ResolutionStrategy.SUGGEST_ALTERNATIVE
                        ],
                        metadata={
                            "required_prep_minutes": required_prep,
                            "available_prep_minutes": available_prep,
                            "prep_deficit": required_prep - available_prep
                        }
                    ))

        return conflicts

    async def _detect_commute_conflicts(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect meetings with insufficient commute time between locations"""
        conflicts = []

        for i in range(len(meetings) - 1):
            current = meetings[i]
            next_meeting = meetings[i + 1]

            current_location = self._normalize_location(current.location)
            next_location = self._normalize_location(next_meeting.location)

            # Skip if both are virtual or same location
            if current_location == next_location or current_location == "virtual" or next_location == "virtual":
                continue

            # Estimate commute time (simplified)
            estimated_commute = self._estimate_commute_time(current_location, next_location)
            available_time = (next_meeting.start_time - current.end_time).total_seconds() / 60

            if available_time < estimated_commute:
                conflicts.append(Conflict(
                    id=f"commute_{current.id}_{next_meeting.id}",
                    type=ConflictType.COMMUTE_TIME_CONFLICT,
                    severity=ConflictSeverity.HIGH,
                    meetings=[current, next_meeting],
                    description=f"Insufficient commute time: need {estimated_commute}min, have {int(available_time)}min",
                    impact_score=(estimated_commute - available_time) / estimated_commute,
                    resolution_strategies=[
                        ResolutionStrategy.AUTO_RESCHEDULE,
                        ResolutionStrategy.SUGGEST_ALTERNATIVE,
                        ResolutionStrategy.REQUEST_CLARIFICATION
                    ],
                    metadata={
                        "from_location": current_location,
                        "to_location": next_location,
                        "estimated_commute_minutes": estimated_commute,
                        "available_minutes": available_time,
                        "commute_deficit": estimated_commute - available_time
                    }
                ))

        return conflicts

    async def _detect_lunch_conflicts(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect meetings that conflict with lunch time"""
        conflicts = []

        lunch_start = 12  # 12 PM
        lunch_end = 13   # 1 PM

        for meeting in meetings:
            meeting_start_hour = meeting.start_time.hour
            meeting_end_hour = meeting.end_time.hour

            # Check if meeting overlaps with lunch time
            if (meeting_start_hour < lunch_end and meeting_end_hour > lunch_start):
                # Check if it's a lunch meeting
                is_lunch_meeting = any(
                    keyword in meeting.title.lower()
                    for keyword in ["lunch", "meal", "eat", "food", "dining"]
                )

                if not is_lunch_meeting:
                    conflicts.append(Conflict(
                        id=f"lunch_{meeting.id}",
                        type=ConflictType.LUNCH_CONFLICT,
                        severity=ConflictSeverity.LOW,
                        meetings=[meeting],
                        description=f"Meeting conflicts with lunch time ({lunch_start}-{lunch_end})",
                        impact_score=0.3,
                        resolution_strategies=[
                            ResolutionStrategy.AUTO_RESCHEDULE,
                            ResolutionStrategy.SUGGEST_ALTERNATIVE
                        ],
                        metadata={
                            "lunch_window": f"{lunch_start:02d}-{lunch_end:02d}",
                            "meeting_start_hour": meeting_start_hour,
                            "meeting_end_hour": meeting_end_hour
                        }
                    ))

        return conflicts

    async def _detect_timezone_conflicts(self, meetings: List[Meeting]) -> List[Conflict]:
        """Detect meetings scheduled at unusual hours due to timezone differences"""
        conflicts = []

        for meeting in meetings:
            hour = meeting.start_time.hour

            # Flag meetings outside normal business hours
            if hour < 8 or hour > 18:
                # Check if it's likely a timezone issue
                has_external_attendees = any(
                    "@" in attendee and not attendee.endswith(".com")  # Simplified check
                    for attendee in (meeting.attendees or [])
                    if isinstance(attendee, str)
                )

                if has_external_attendees:
                    severity = ConflictSeverity.HIGH if hour < 7 or hour > 20 else ConflictSeverity.MEDIUM

                    conflicts.append(Conflict(
                        id=f"timezone_{meeting.id}",
                        type=ConflictType.TIMEZONE_CONFLICT,
                        severity=severity,
                        meetings=[meeting],
                        description=f"Meeting at unusual hour ({hour:02d}:00) likely due to timezone differences",
                        impact_score=0.6 if hour < 7 or hour > 20 else 0.4,
                        resolution_strategies=[
                            ResolutionStrategy.SUGGEST_ALTERNATIVE,
                            ResolutionStrategy.REQUEST_CLARIFICATION
                        ],
                        metadata={
                            "meeting_hour": hour,
                            "has_external_attendees": has_external_attendees,
                            "timezone": meeting.timezone
                        }
                    ))

        return conflicts

    def _meetings_overlap(self, meeting1: Meeting, meeting2: Meeting) -> bool:
        """Check if two meetings overlap in time"""
        return meeting1.start_time < meeting2.end_time and meeting1.end_time > meeting2.start_time

    def _calculate_overlap_minutes(self, meeting1: Meeting, meeting2: Meeting) -> int:
        """Calculate overlap duration in minutes"""
        overlap_start = max(meeting1.start_time, meeting2.start_time)
        overlap_end = min(meeting1.end_time, meeting2.end_time)
        return int((overlap_end - overlap_start).total_seconds() / 60)

    def _determine_overlap_severity(self, overlap_minutes: int) -> ConflictSeverity:
        """Determine conflict severity based on overlap duration"""
        rules = self.conflict_rules[ConflictType.DIRECT_OVERLAP]["severity_thresholds"]

        for threshold, severity in sorted(rules.items()):
            if overlap_minutes >= threshold:
                return severity

        return ConflictSeverity.LOW

    def _determine_buffer_severity(self, gap_minutes: float) -> ConflictSeverity:
        """Determine buffer conflict severity"""
        rules = self.conflict_rules[ConflictType.INSUFFICIENT_BUFFER]["severity_thresholds"]

        for threshold, severity in sorted(rules.items(), reverse=True):
            if gap_minutes <= threshold:
                return severity

        return ConflictSeverity.LOW

    def _normalize_location(self, location: Optional[str]) -> str:
        """Normalize location for comparison"""
        if not location:
            return "unknown"

        location = location.lower().strip()

        # Check for virtual meeting indicators
        virtual_indicators = ["zoom", "teams", "meet", "skype", "webex", "virtual", "online", "call"]
        if any(indicator in location for indicator in virtual_indicators):
            return "virtual"

        return location

    def _estimate_commute_time(self, from_location: str, to_location: str) -> int:
        """Estimate commute time between locations (simplified)"""
        # This is a simplified estimation
        # In production, you'd use a mapping service API

        if from_location == to_location:
            return 0

        if "virtual" in from_location or "virtual" in to_location:
            return 0

        # Default estimates
        if "building" in from_location and "building" in to_location:
            return 10  # Same campus/area
        else:
            return 30  # Different locations


class ConflictResolver:
    """Advanced conflict resolution system"""

    def __init__(self):
        self.calendar_client = google_calendar_client
        self.oauth_service = oauth_service
        self.autonomous_manager = autonomous_calendar_manager

    async def create_resolution_plan(
        self,
        conflict: Conflict,
        user: User,
        db: AsyncSession
    ) -> ResolutionPlan:
        """Create a resolution plan for a conflict"""

        strategy = await self._select_best_strategy(conflict, user, db)
        actions = await self._generate_actions(conflict, strategy, user, db)

        return ResolutionPlan(
            conflict_id=conflict.id,
            strategy=strategy,
            actions=actions,
            estimated_success_rate=await self._estimate_success_rate(strategy, conflict),
            estimated_impact=await self._estimate_resolution_impact(strategy, conflict),
            required_permissions=await self._get_required_permissions(strategy),
            user_approval_required=await self._requires_user_approval(strategy, conflict)
        )

    async def execute_resolution(
        self,
        resolution_plan: ResolutionPlan,
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Execute a resolution plan"""

        results = {
            "success": False,
            "executed_actions": [],
            "failed_actions": [],
            "partial_success": False
        }

        access_token = await self.oauth_service.get_valid_access_token(user, db)
        if not access_token:
            results["failed_actions"].append("No valid access token")
            return results

        for action in resolution_plan.actions:
            try:
                action_result = await self._execute_action(action, user, access_token, db)
                if action_result["success"]:
                    results["executed_actions"].append(action_result)
                else:
                    results["failed_actions"].append(action_result)
            except Exception as e:
                logger.error(f"Failed to execute action {action['type']}: {e}")
                results["failed_actions"].append({
                    "action": action,
                    "error": str(e)
                })

        results["success"] = len(results["executed_actions"]) == len(resolution_plan.actions)
        results["partial_success"] = len(results["executed_actions"]) > 0

        return results

    async def _select_best_strategy(
        self,
        conflict: Conflict,
        user: User,
        db: AsyncSession
    ) -> ResolutionStrategy:
        """Select the best resolution strategy for a conflict"""

        # Strategy selection based on conflict type and context
        strategy_scores = {}

        for strategy in conflict.resolution_strategies:
            score = await self._score_strategy(strategy, conflict, user, db)
            strategy_scores[strategy] = score

        # Select highest scoring strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        return best_strategy

    async def _score_strategy(
        self,
        strategy: ResolutionStrategy,
        conflict: Conflict,
        user: User,
        db: AsyncSession
    ) -> float:
        """Score a resolution strategy"""

        base_score = 0.5

        # Strategy-specific scoring
        if strategy == ResolutionStrategy.AUTO_RESCHEDULE:
            # Higher score for high-importance meetings
            avg_importance = sum(
                m.ai_importance_score or 0.5 for m in conflict.meetings
            ) / len(conflict.meetings)
            base_score += avg_importance * 0.3

        elif strategy == ResolutionStrategy.AUTO_DECLINE:
            # Higher score for low-importance meetings
            avg_importance = sum(
                m.ai_importance_score or 0.5 for m in conflict.meetings
            ) / len(conflict.meetings)
            base_score += (1.0 - avg_importance) * 0.4

        elif strategy == ResolutionStrategy.CREATE_BUFFER:
            # Good for buffer conflicts
            if conflict.type == ConflictType.INSUFFICIENT_BUFFER:
                base_score += 0.3

        elif strategy == ResolutionStrategy.OPTIMIZE_SCHEDULE:
            # Good for overloaded days
            if conflict.type == ConflictType.OVERLOADED_DAY:
                base_score += 0.4

        # Adjust based on conflict severity
        severity_multiplier = {
            ConflictSeverity.LOW: 0.8,
            ConflictSeverity.MEDIUM: 1.0,
            ConflictSeverity.HIGH: 1.2,
            ConflictSeverity.CRITICAL: 1.5
        }
        base_score *= severity_multiplier[conflict.severity]

        return min(base_score, 1.0)

    async def _generate_actions(
        self,
        conflict: Conflict,
        strategy: ResolutionStrategy,
        user: User,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generate specific actions for a resolution strategy"""

        actions = []

        if strategy == ResolutionStrategy.AUTO_RESCHEDULE:
            # Find alternative times using genetic algorithm
            alternatives = await genetic_scheduler.find_optimal_slots(
                conflict.meetings, user, db
            )

            for i, meeting in enumerate(conflict.meetings):
                if i < len(alternatives):
                    actions.append({
                        "type": "reschedule_meeting",
                        "meeting_id": meeting.id,
                        "new_start_time": alternatives[i]["start_time"],
                        "new_end_time": alternatives[i]["end_time"],
                        "reason": f"Resolving {conflict.type.value} conflict"
                    })

        elif strategy == ResolutionStrategy.AUTO_DECLINE:
            # Decline lowest importance meeting
            lowest_importance_meeting = min(
                conflict.meetings,
                key=lambda m: m.ai_importance_score or 0.5
            )

            actions.append({
                "type": "decline_meeting",
                "meeting_id": lowest_importance_meeting.id,
                "reason": conflict.description
            })

        elif strategy == ResolutionStrategy.CREATE_BUFFER:
            if conflict.type == ConflictType.INSUFFICIENT_BUFFER:
                buffer_minutes = conflict.metadata.get("buffer_deficit", 15)
                actions.append({
                    "type": "create_buffer",
                    "before_meeting_id": conflict.meetings[1].id,
                    "buffer_minutes": int(buffer_minutes)
                })

        elif strategy == ResolutionStrategy.SUGGEST_ALTERNATIVE:
            # Generate alternative time suggestions
            for meeting in conflict.meetings:
                alternatives = await self._find_alternative_times(meeting, user, db)
                actions.append({
                    "type": "suggest_alternatives",
                    "meeting_id": meeting.id,
                    "alternatives": alternatives
                })

        return actions

    async def _execute_action(
        self,
        action: Dict[str, Any],
        user: User,
        access_token: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Execute a specific action"""

        action_type = action["type"]
        result = {"success": False, "action_type": action_type}

        try:
            if action_type == "reschedule_meeting":
                meeting_id = action["meeting_id"]
                new_start = datetime.fromisoformat(action["new_start_time"])
                new_end = datetime.fromisoformat(action["new_end_time"])

                # Get meeting
                meeting_result = await db.execute(
                    select(Meeting).where(Meeting.id == meeting_id)
                )
                meeting = meeting_result.scalar_one_or_none()

                if meeting and meeting.google_event_id:
                    success = await self.autonomous_manager.reschedule_meeting(
                        access_token,
                        meeting.google_event_id,
                        new_start,
                        new_end,
                        meeting.calendar_id or "primary"
                    )

                    if success:
                        # Update database
                        meeting.start_time = new_start
                        meeting.end_time = new_end
                        meeting.updated_at = datetime.utcnow()
                        await db.commit()

                        result["success"] = True
                        result["details"] = f"Rescheduled to {new_start.isoformat()}"

            elif action_type == "decline_meeting":
                meeting_id = action["meeting_id"]
                reason = action.get("reason", "Calendar conflict")

                # Get meeting
                meeting_result = await db.execute(
                    select(Meeting).where(Meeting.id == meeting_id)
                )
                meeting = meeting_result.scalar_one_or_none()

                if meeting and meeting.google_event_id:
                    success = await self.autonomous_manager.auto_decline_meeting(
                        access_token,
                        meeting.google_event_id,
                        reason,
                        meeting.calendar_id or "primary"
                    )

                    if success:
                        meeting.status = MeetingStatus.CANCELLED
                        meeting.ai_decision = AIDecisionType.AUTO_DECLINE
                        meeting.ai_decision_reasoning = reason
                        await db.commit()

                        result["success"] = True
                        result["details"] = f"Declined meeting: {reason}"

            elif action_type == "create_buffer":
                buffer_minutes = action.get("buffer_minutes", 15)
                before_meeting_id = action.get("before_meeting_id")

                buffer_events = await self.autonomous_manager.create_buffer_time(
                    access_token,
                    before_event_id=before_meeting_id,
                    buffer_minutes=buffer_minutes,
                    calendar_id="primary"
                )

                if buffer_events:
                    result["success"] = True
                    result["details"] = f"Created {buffer_minutes}min buffer"
                    result["buffer_event_ids"] = buffer_events

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error executing action {action_type}: {e}")

        return result

    async def _find_alternative_times(
        self,
        meeting: Meeting,
        user: User,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Find alternative times for a meeting"""

        duration = meeting.end_time - meeting.start_time
        original_date = meeting.start_time.date()

        alternatives = []

        # Try different times on the same day
        good_times = [(10, 0), (14, 0), (15, 30), (11, 0), (16, 0)]

        for hour, minute in good_times:
            alt_start = datetime.combine(
                original_date,
                datetime.min.time().replace(hour=hour, minute=minute)
            ).replace(tzinfo=timezone.utc)
            alt_end = alt_start + duration

            # Skip if this is too close to original time
            if abs((alt_start - meeting.start_time).total_seconds()) < 3600:  # 1 hour
                continue

            alternatives.append({
                "start_time": alt_start.isoformat(),
                "end_time": alt_end.isoformat(),
                "reason": f"Alternative slot at {hour:02d}:{minute:02d}"
            })

            if len(alternatives) >= 3:
                break

        return alternatives

    async def _estimate_success_rate(
        self,
        strategy: ResolutionStrategy,
        conflict: Conflict
    ) -> float:
        """Estimate success rate of a resolution strategy"""

        base_rates = {
            ResolutionStrategy.AUTO_RESCHEDULE: 0.8,
            ResolutionStrategy.AUTO_DECLINE: 0.9,
            ResolutionStrategy.CREATE_BUFFER: 0.95,
            ResolutionStrategy.SUGGEST_ALTERNATIVE: 0.7,
            ResolutionStrategy.OPTIMIZE_SCHEDULE: 0.6
        }

        base_rate = base_rates.get(strategy, 0.5)

        # Adjust based on conflict severity
        if conflict.severity == ConflictSeverity.CRITICAL:
            base_rate *= 0.8
        elif conflict.severity == ConflictSeverity.LOW:
            base_rate *= 1.1

        return min(base_rate, 1.0)

    async def _estimate_resolution_impact(
        self,
        strategy: ResolutionStrategy,
        conflict: Conflict
    ) -> float:
        """Estimate the positive impact of resolving the conflict"""
        return conflict.impact_score * 0.9  # Assume 90% of conflict impact is resolved

    async def _get_required_permissions(self, strategy: ResolutionStrategy) -> List[str]:
        """Get required permissions for a strategy"""
        permission_map = {
            ResolutionStrategy.AUTO_RESCHEDULE: ["calendar.events.write"],
            ResolutionStrategy.AUTO_DECLINE: ["calendar.events.write"],
            ResolutionStrategy.CREATE_BUFFER: ["calendar.events.write"],
            ResolutionStrategy.SUGGEST_ALTERNATIVE: [],
            ResolutionStrategy.OPTIMIZE_SCHEDULE: ["calendar.events.write"]
        }
        return permission_map.get(strategy, [])

    async def _requires_user_approval(
        self,
        strategy: ResolutionStrategy,
        conflict: Conflict
    ) -> bool:
        """Check if strategy requires user approval"""
        high_impact_strategies = [
            ResolutionStrategy.AUTO_DECLINE,
            ResolutionStrategy.AUTO_RESCHEDULE
        ]

        return (strategy in high_impact_strategies and
                conflict.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL])


# Global instances
conflict_detector = ConflictDetector()
conflict_resolver = ConflictResolver()