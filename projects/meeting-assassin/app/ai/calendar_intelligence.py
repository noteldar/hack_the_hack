"""
Advanced Calendar Pattern Recognition and Optimization System
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta, time
import logging
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of calendar patterns"""
    MEETING_CLUSTER = "meeting_cluster"
    FOCUS_TIME_BLOCK = "focus_time_block"
    RECURRING_SERIES = "recurring_series"
    MEETING_FATIGUE_ZONE = "meeting_fatigue_zone"
    OPTIMAL_SLOT = "optimal_slot"
    COLLABORATION_WINDOW = "collaboration_window"
    DEEP_WORK_ZONE = "deep_work_zone"
    BUFFER_TIME = "buffer_time"


class TimePreference(Enum):
    """User time preferences"""
    MORNING_PERSON = "morning_person"
    AFTERNOON_PEAK = "afternoon_peak"
    EVENING_WORKER = "evening_worker"
    FLEXIBLE = "flexible"


@dataclass
class CalendarPattern:
    """Identified calendar pattern"""
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    time_range: Tuple[time, time]  # Start and end time
    days_of_week: List[int]  # 0=Monday, 6=Sunday
    frequency: str  # daily, weekly, monthly
    impact_score: float  # -1.0 (negative) to 1.0 (positive)
    description: str
    recommendations: List[str]
    affected_meetings: List[str]  # Meeting IDs
    optimization_potential: float  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'pattern_type': self.pattern_type.value,
            'time_range': [t.isoformat() for t in self.time_range]
        }


@dataclass
class ProductivityInsight:
    """Productivity insights from calendar analysis"""
    focus_time_ratio: float  # Ratio of focus time to meeting time
    meeting_efficiency_score: float  # 0.0 to 1.0
    context_switching_penalty: float  # Time lost to context switching
    optimal_meeting_duration: int  # Minutes
    peak_productivity_hours: List[Tuple[int, int]]  # List of (start_hour, end_hour)
    meeting_fatigue_threshold: int  # Max meetings per day before fatigue
    collaboration_effectiveness: float  # 0.0 to 1.0
    time_reclamation_opportunities: List[Dict[str, Any]]
    weekly_productivity_score: float  # 0.0 to 100.0
    improvement_suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class CalendarIntelligence:
    """Advanced calendar pattern recognition and optimization"""

    def __init__(self):
        self.patterns_cache = {}
        self.user_preferences = {}
        self.historical_data = []
        self.optimization_history = []

    async def analyze_calendar_patterns(
        self,
        meetings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Comprehensive calendar pattern analysis
        """
        try:
            # Prepare meeting data
            meeting_df = self._prepare_meeting_dataframe(meetings)

            if meeting_df.empty:
                return self._empty_analysis_result()

            # Identify various patterns
            patterns = []

            # 1. Find meeting clusters
            clusters = await self._identify_meeting_clusters(meeting_df)
            patterns.extend(clusters)

            # 2. Identify focus time blocks
            focus_blocks = await self._identify_focus_time_blocks(meeting_df)
            patterns.extend(focus_blocks)

            # 3. Detect recurring patterns
            recurring = await self._detect_recurring_patterns(meeting_df)
            patterns.extend(recurring)

            # 4. Find meeting fatigue zones
            fatigue_zones = await self._identify_fatigue_zones(meeting_df)
            patterns.extend(fatigue_zones)

            # 5. Calculate productivity insights
            productivity_insight = await self._calculate_productivity_insights(
                meeting_df,
                patterns,
                user_context
            )

            # 6. Generate optimization recommendations
            optimizations = await self._generate_optimizations(
                patterns,
                productivity_insight,
                meeting_df
            )

            # 7. Predict future patterns
            predictions = await self._predict_future_patterns(meeting_df, patterns)

            return {
                "patterns": [p.to_dict() for p in patterns],
                "productivity_insight": productivity_insight.to_dict(),
                "optimizations": optimizations,
                "predictions": predictions,
                "summary": self._generate_summary(patterns, productivity_insight),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Calendar pattern analysis failed: {e}")
            return self._empty_analysis_result()

    def _prepare_meeting_dataframe(self, meetings: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare meeting data for analysis"""

        if not meetings:
            return pd.DataFrame()

        # Extract relevant features
        data = []
        for meeting in meetings:
            try:
                start_time = datetime.fromisoformat(meeting.get("start_time", ""))
                end_time = datetime.fromisoformat(meeting.get("end_time", ""))
                duration = (end_time - start_time).total_seconds() / 60  # minutes

                data.append({
                    "id": meeting.get("id"),
                    "title": meeting.get("title", ""),
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_minutes": duration,
                    "hour": start_time.hour,
                    "day_of_week": start_time.weekday(),
                    "date": start_time.date(),
                    "attendee_count": len(meeting.get("attendees", [])),
                    "is_recurring": meeting.get("is_recurring", False),
                    "importance_score": meeting.get("ai_importance_score", 0.5),
                    "meeting_type": meeting.get("meeting_type", "unknown")
                })
            except Exception as e:
                logger.warning(f"Failed to process meeting: {e}")
                continue

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df.sort_values("start_time")
        return df

    async def _identify_meeting_clusters(self, df: pd.DataFrame) -> List[CalendarPattern]:
        """Identify clusters of back-to-back meetings"""

        patterns = []

        # Group meetings by date
        for date, day_meetings in df.groupby("date"):
            day_meetings = day_meetings.sort_values("start_time")

            # Find clusters (meetings within 30 minutes of each other)
            clusters = []
            current_cluster = []

            for idx, meeting in day_meetings.iterrows():
                if not current_cluster:
                    current_cluster = [meeting]
                else:
                    last_meeting = current_cluster[-1]
                    gap = (meeting["start_time"] - last_meeting["end_time"]).total_seconds() / 60

                    if gap <= 30:  # 30-minute threshold
                        current_cluster.append(meeting)
                    else:
                        if len(current_cluster) >= 3:  # At least 3 meetings to be a cluster
                            clusters.append(current_cluster)
                        current_cluster = [meeting]

            # Check last cluster
            if len(current_cluster) >= 3:
                clusters.append(current_cluster)

            # Create pattern for each cluster
            for cluster in clusters:
                start_time = cluster[0]["start_time"].time()
                end_time = cluster[-1]["end_time"].time()
                total_duration = sum(m["duration_minutes"] for m in cluster)

                pattern = CalendarPattern(
                    pattern_type=PatternType.MEETING_CLUSTER,
                    confidence=0.9,
                    time_range=(start_time, end_time),
                    days_of_week=[date.weekday()],
                    frequency="daily",
                    impact_score=-0.7,  # Negative impact due to fatigue
                    description=f"Cluster of {len(cluster)} back-to-back meetings ({total_duration:.0f} minutes total)",
                    recommendations=[
                        "Consider adding buffer time between meetings",
                        "Consolidate related meetings",
                        "Schedule breaks for mental reset"
                    ],
                    affected_meetings=[str(m["id"]) for m in cluster],
                    optimization_potential=0.8
                )
                patterns.append(pattern)

        return patterns

    async def _identify_focus_time_blocks(self, df: pd.DataFrame) -> List[CalendarPattern]:
        """Identify potential focus time blocks"""

        patterns = []

        # Find common free time slots
        hour_occupancy = defaultdict(list)

        for _, meeting in df.iterrows():
            start_hour = meeting["start_time"].hour
            end_hour = meeting["end_time"].hour
            day = meeting["day_of_week"]

            for hour in range(start_hour, min(end_hour + 1, 24)):
                hour_occupancy[(day, hour)].append(meeting["id"])

        # Find consistently free blocks
        all_days = df["day_of_week"].unique()
        for hour in range(8, 18):  # Business hours
            free_days = []
            for day in all_days:
                if (day, hour) not in hour_occupancy or len(hour_occupancy[(day, hour)]) == 0:
                    free_days.append(day)

            if len(free_days) >= 3:  # Free on at least 3 days
                pattern = CalendarPattern(
                    pattern_type=PatternType.FOCUS_TIME_BLOCK,
                    confidence=0.7,
                    time_range=(time(hour, 0), time(hour + 1, 0)),
                    days_of_week=free_days,
                    frequency="weekly",
                    impact_score=0.9,  # Positive impact
                    description=f"Potential focus time block at {hour}:00-{hour+1}:00",
                    recommendations=[
                        "Block this time for deep work",
                        "Decline non-critical meetings during this slot",
                        "Use for high-concentration tasks"
                    ],
                    affected_meetings=[],
                    optimization_potential=0.9
                )
                patterns.append(pattern)

        return patterns

    async def _detect_recurring_patterns(self, df: pd.DataFrame) -> List[CalendarPattern]:
        """Detect recurring meeting patterns"""

        patterns = []

        # Group by meeting title similarity
        title_groups = defaultdict(list)
        for _, meeting in df.iterrows():
            # Simple grouping by title words
            key_words = set(meeting["title"].lower().split()[:3])  # First 3 words
            key = " ".join(sorted(key_words))
            title_groups[key].append(meeting)

        # Analyze each group for patterns
        for title_key, meetings in title_groups.items():
            if len(meetings) < 3:  # Need at least 3 occurrences
                continue

            # Check if they occur on same day/time
            day_time_counts = Counter()
            for meeting in meetings:
                day_time = (meeting["day_of_week"], meeting["hour"])
                day_time_counts[day_time] += 1

            # Find most common day/time
            if day_time_counts:
                most_common = day_time_counts.most_common(1)[0]
                (day, hour), count = most_common

                if count >= 2:  # At least 2 occurrences at same time
                    avg_duration = np.mean([m["duration_minutes"] for m in meetings])

                    pattern = CalendarPattern(
                        pattern_type=PatternType.RECURRING_SERIES,
                        confidence=count / len(meetings),
                        time_range=(time(hour, 0), time(hour + int(avg_duration // 60), int(avg_duration % 60))),
                        days_of_week=[day],
                        frequency="weekly",
                        impact_score=0.0,  # Neutral - depends on meeting value
                        description=f"Recurring meeting pattern: '{title_key}' on day {day} at {hour}:00",
                        recommendations=[
                            f"Optimize duration (current avg: {avg_duration:.0f} min)",
                            "Consider if all instances are necessary",
                            "Batch similar topics together"
                        ],
                        affected_meetings=[str(m["id"]) for m in meetings],
                        optimization_potential=0.6
                    )
                    patterns.append(pattern)

        return patterns

    async def _identify_fatigue_zones(self, df: pd.DataFrame) -> List[CalendarPattern]:
        """Identify meeting fatigue zones"""

        patterns = []

        # Calculate meeting density by hour
        hour_density = defaultdict(list)
        for _, meeting in df.iterrows():
            hour = meeting["hour"]
            hour_density[hour].append(meeting["duration_minutes"])

        # Find high-density zones
        fatigue_hours = []
        for hour in range(8, 18):
            if hour in hour_density:
                meeting_count = len(hour_density[hour])
                total_minutes = sum(hour_density[hour])

                # High density: >3 meetings or >120 minutes in an hour span
                if meeting_count > 3 or total_minutes > 120:
                    fatigue_hours.append(hour)

        # Create continuous zones
        if fatigue_hours:
            zones = []
            current_zone = [fatigue_hours[0]]

            for hour in fatigue_hours[1:]:
                if hour == current_zone[-1] + 1:
                    current_zone.append(hour)
                else:
                    if len(current_zone) >= 2:
                        zones.append(current_zone)
                    current_zone = [hour]

            if len(current_zone) >= 2:
                zones.append(current_zone)

            # Create patterns for zones
            for zone in zones:
                pattern = CalendarPattern(
                    pattern_type=PatternType.MEETING_FATIGUE_ZONE,
                    confidence=0.8,
                    time_range=(time(zone[0], 0), time(zone[-1] + 1, 0)),
                    days_of_week=list(range(5)),  # Weekdays
                    frequency="daily",
                    impact_score=-0.8,  # Negative impact
                    description=f"High meeting density zone: {zone[0]}:00-{zone[-1]+1}:00",
                    recommendations=[
                        "Distribute meetings more evenly",
                        "Add mandatory breaks between meetings",
                        "Limit meeting duration in this zone",
                        "Consider async alternatives"
                    ],
                    affected_meetings=[],
                    optimization_potential=0.85
                )
                patterns.append(pattern)

        return patterns

    async def _calculate_productivity_insights(
        self,
        df: pd.DataFrame,
        patterns: List[CalendarPattern],
        user_context: Optional[Dict[str, Any]]
    ) -> ProductivityInsight:
        """Calculate comprehensive productivity insights"""

        # Calculate focus time ratio
        total_hours = len(df["date"].unique()) * 8  # Assuming 8-hour workday
        meeting_hours = df["duration_minutes"].sum() / 60
        focus_time_ratio = max(0, (total_hours - meeting_hours) / total_hours)

        # Calculate meeting efficiency
        short_meetings = len(df[df["duration_minutes"] <= 30])
        total_meetings = len(df)
        meeting_efficiency_score = short_meetings / total_meetings if total_meetings > 0 else 0.5

        # Estimate context switching penalty
        context_switches = 0
        for date, day_meetings in df.groupby("date"):
            day_meetings = day_meetings.sort_values("start_time")
            for i in range(1, len(day_meetings)):
                gap = (day_meetings.iloc[i]["start_time"] - day_meetings.iloc[i-1]["end_time"]).total_seconds() / 60
                if gap < 30:  # Less than 30 minutes between meetings
                    context_switches += 1

        context_switching_penalty = context_switches * 15  # 15 minutes per switch

        # Calculate optimal meeting duration
        if not df.empty:
            optimal_meeting_duration = int(df["duration_minutes"].quantile(0.25))  # 25th percentile
        else:
            optimal_meeting_duration = 30

        # Identify peak productivity hours (hours with fewest meetings)
        hour_counts = df["hour"].value_counts()
        all_hours = set(range(8, 18))
        meeting_hours_set = set(hour_counts.index)
        free_hours = sorted(all_hours - meeting_hours_set)

        peak_productivity_hours = []
        if free_hours:
            # Group consecutive hours
            current_block = [free_hours[0]]
            for hour in free_hours[1:]:
                if hour == current_block[-1] + 1:
                    current_block.append(hour)
                else:
                    if len(current_block) >= 2:
                        peak_productivity_hours.append((current_block[0], current_block[-1]))
                    current_block = [hour]
            if len(current_block) >= 2:
                peak_productivity_hours.append((current_block[0], current_block[-1]))

        # Calculate meeting fatigue threshold
        daily_meeting_counts = df.groupby("date").size()
        meeting_fatigue_threshold = int(daily_meeting_counts.quantile(0.75)) if not daily_meeting_counts.empty else 5

        # Calculate collaboration effectiveness
        small_meetings = len(df[df["attendee_count"] <= 5])
        collaboration_effectiveness = small_meetings / total_meetings if total_meetings > 0 else 0.7

        # Identify time reclamation opportunities
        time_reclamation_opportunities = []

        # Low-importance long meetings
        long_low_importance = df[(df["duration_minutes"] > 45) & (df["importance_score"] < 0.5)]
        for _, meeting in long_low_importance.iterrows():
            time_reclamation_opportunities.append({
                "meeting_id": str(meeting["id"]),
                "title": meeting["title"],
                "potential_time_saved": meeting["duration_minutes"] - 30,
                "action": "Reduce duration or convert to async"
            })

        # Calculate weekly productivity score
        weekly_productivity_score = (
            focus_time_ratio * 30 +
            meeting_efficiency_score * 20 +
            collaboration_effectiveness * 20 +
            (1 - min(context_switches / 20, 1)) * 30  # Penalize excessive context switching
        )

        # Generate improvement suggestions
        improvement_suggestions = []

        if focus_time_ratio < 0.3:
            improvement_suggestions.append("Increase focus time by declining low-priority meetings")

        if meeting_efficiency_score < 0.5:
            improvement_suggestions.append("Shorten meeting durations - aim for 30-minute defaults")

        if context_switches > 10:
            improvement_suggestions.append("Batch meetings together to reduce context switching")

        if not peak_productivity_hours:
            improvement_suggestions.append("Block out 2-hour windows for deep work")

        if collaboration_effectiveness < 0.5:
            improvement_suggestions.append("Reduce attendee lists to essential participants only")

        return ProductivityInsight(
            focus_time_ratio=focus_time_ratio,
            meeting_efficiency_score=meeting_efficiency_score,
            context_switching_penalty=context_switching_penalty,
            optimal_meeting_duration=optimal_meeting_duration,
            peak_productivity_hours=peak_productivity_hours,
            meeting_fatigue_threshold=meeting_fatigue_threshold,
            collaboration_effectiveness=collaboration_effectiveness,
            time_reclamation_opportunities=time_reclamation_opportunities,
            weekly_productivity_score=weekly_productivity_score,
            improvement_suggestions=improvement_suggestions
        )

    async def _generate_optimizations(
        self,
        patterns: List[CalendarPattern],
        productivity_insight: ProductivityInsight,
        df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations"""

        optimizations = []

        # 1. Meeting consolidation opportunities
        recurring_patterns = [p for p in patterns if p.pattern_type == PatternType.RECURRING_SERIES]
        if len(recurring_patterns) > 1:
            optimizations.append({
                "type": "consolidation",
                "priority": "high",
                "title": "Consolidate recurring meetings",
                "description": f"Found {len(recurring_patterns)} recurring meeting patterns that could be combined",
                "potential_time_saved": len(recurring_patterns) * 15,  # 15 minutes each
                "implementation": [
                    "Review recurring meeting purposes",
                    "Combine similar topics into single sessions",
                    "Create shared agendas"
                ]
            })

        # 2. Focus time protection
        if productivity_insight.focus_time_ratio < 0.4:
            optimizations.append({
                "type": "focus_time",
                "priority": "critical",
                "title": "Protect focus time blocks",
                "description": f"Only {productivity_insight.focus_time_ratio:.1%} of time available for focused work",
                "potential_time_saved": 120,  # 2 hours daily
                "implementation": [
                    "Block 9-11 AM for deep work",
                    "Set 'Do Not Disturb' during focus blocks",
                    "Batch meetings in afternoon"
                ]
            })

        # 3. Meeting duration optimization
        long_meetings = df[df["duration_minutes"] > 60]
        if len(long_meetings) > 0:
            total_excess = long_meetings["duration_minutes"].sum() - len(long_meetings) * 45
            optimizations.append({
                "type": "duration",
                "priority": "medium",
                "title": "Reduce meeting durations",
                "description": f"{len(long_meetings)} meetings exceed 60 minutes",
                "potential_time_saved": int(total_excess),
                "implementation": [
                    "Set default meeting duration to 30 minutes",
                    "Require agenda for meetings >30 minutes",
                    "Use timer to keep meetings on track"
                ]
            })

        # 4. Meeting-free zones
        fatigue_zones = [p for p in patterns if p.pattern_type == PatternType.MEETING_FATIGUE_ZONE]
        if fatigue_zones:
            optimizations.append({
                "type": "meeting_free_zone",
                "priority": "high",
                "title": "Establish meeting-free zones",
                "description": f"Identified {len(fatigue_zones)} high-fatigue time zones",
                "potential_time_saved": 90,  # 1.5 hours
                "implementation": [
                    "Declare Fridays meeting-free",
                    "No meetings before 9 AM",
                    "Limit daily meetings to 4 maximum"
                ]
            })

        # 5. Async alternatives
        status_meetings = df[df["title"].str.lower().str.contains("status|update|sync", na=False)]
        if len(status_meetings) > 0:
            optimizations.append({
                "type": "async",
                "priority": "medium",
                "title": "Convert status updates to async",
                "description": f"{len(status_meetings)} status meetings could be written updates",
                "potential_time_saved": len(status_meetings) * 30,
                "implementation": [
                    "Use Slack/Teams for status updates",
                    "Create weekly written reports",
                    "Record video updates when needed"
                ]
            })

        return optimizations

    async def _predict_future_patterns(
        self,
        df: pd.DataFrame,
        patterns: List[CalendarPattern]
    ) -> Dict[str, Any]:
        """Predict future calendar patterns"""

        predictions = {
            "next_week_forecast": {},
            "optimization_impact": {},
            "risk_areas": []
        }

        if df.empty:
            return predictions

        # Predict next week's meeting load
        avg_daily_meetings = df.groupby("date").size().mean()
        avg_daily_duration = df.groupby("date")["duration_minutes"].sum().mean()

        predictions["next_week_forecast"] = {
            "expected_meetings": int(avg_daily_meetings * 5),  # 5 workdays
            "expected_hours": round(avg_daily_duration * 5 / 60, 1),
            "fatigue_risk": "high" if avg_daily_meetings > 6 else "medium" if avg_daily_meetings > 4 else "low",
            "recommended_declines": max(0, int((avg_daily_meetings - 4) * 5))  # Keep to 4 meetings/day
        }

        # Predict optimization impact
        total_optimization_potential = sum(p.optimization_potential for p in patterns)
        predictions["optimization_impact"] = {
            "potential_time_saved_weekly": int(total_optimization_potential * 60),  # minutes
            "productivity_improvement": f"{min(total_optimization_potential * 20, 40):.0f}%",
            "stress_reduction": "significant" if total_optimization_potential > 3 else "moderate"
        }

        # Identify risk areas
        if avg_daily_meetings > 6:
            predictions["risk_areas"].append({
                "risk": "Meeting overload",
                "likelihood": "high",
                "mitigation": "Implement strict meeting criteria"
            })

        fatigue_patterns = [p for p in patterns if p.pattern_type == PatternType.MEETING_FATIGUE_ZONE]
        if fatigue_patterns:
            predictions["risk_areas"].append({
                "risk": "Burnout from meeting clusters",
                "likelihood": "medium",
                "mitigation": "Enforce breaks between meetings"
            })

        focus_blocks = [p for p in patterns if p.pattern_type == PatternType.FOCUS_TIME_BLOCK]
        if not focus_blocks:
            predictions["risk_areas"].append({
                "risk": "No protected focus time",
                "likelihood": "high",
                "mitigation": "Block daily 2-hour focus windows"
            })

        return predictions

    def _generate_summary(
        self,
        patterns: List[CalendarPattern],
        productivity_insight: ProductivityInsight
    ) -> str:
        """Generate executive summary of analysis"""

        summary_parts = []

        # Overall productivity score
        summary_parts.append(
            f"Weekly Productivity Score: {productivity_insight.weekly_productivity_score:.0f}/100"
        )

        # Key findings
        if productivity_insight.focus_time_ratio < 0.3:
            summary_parts.append(
                f"CRITICAL: Only {productivity_insight.focus_time_ratio:.0%} focus time available"
            )

        meeting_clusters = [p for p in patterns if p.pattern_type == PatternType.MEETING_CLUSTER]
        if meeting_clusters:
            summary_parts.append(
                f"Found {len(meeting_clusters)} problematic meeting clusters causing fatigue"
            )

        # Top recommendation
        if productivity_insight.improvement_suggestions:
            summary_parts.append(
                f"Top priority: {productivity_insight.improvement_suggestions[0]}"
            )

        # Time savings potential
        if productivity_insight.time_reclamation_opportunities:
            total_savings = sum(
                opp["potential_time_saved"]
                for opp in productivity_insight.time_reclamation_opportunities
            )
            summary_parts.append(
                f"Potential time savings: {total_savings} minutes per week"
            )

        return " | ".join(summary_parts)

    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result"""
        return {
            "patterns": [],
            "productivity_insight": ProductivityInsight(
                focus_time_ratio=0.5,
                meeting_efficiency_score=0.5,
                context_switching_penalty=0,
                optimal_meeting_duration=30,
                peak_productivity_hours=[],
                meeting_fatigue_threshold=5,
                collaboration_effectiveness=0.5,
                time_reclamation_opportunities=[],
                weekly_productivity_score=50,
                improvement_suggestions=["Insufficient data for analysis"]
            ).to_dict(),
            "optimizations": [],
            "predictions": {},
            "summary": "Insufficient calendar data for pattern analysis",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    async def get_time_slot_quality(
        self,
        proposed_time: datetime,
        duration_minutes: int,
        existing_meetings: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a proposed time slot
        """

        quality_score = 100.0  # Start with perfect score

        # Check for conflicts
        proposed_end = proposed_time + timedelta(minutes=duration_minutes)
        for meeting in existing_meetings:
            meeting_start = datetime.fromisoformat(meeting.get("start_time", ""))
            meeting_end = datetime.fromisoformat(meeting.get("end_time", ""))

            # Direct conflict
            if (proposed_time < meeting_end and proposed_end > meeting_start):
                return {
                    "quality_score": 0,
                    "is_available": False,
                    "conflict": True,
                    "reason": "Direct conflict with existing meeting"
                }

            # Check for buffer time (15 minutes before/after)
            buffer = timedelta(minutes=15)
            if (proposed_time - buffer < meeting_end and proposed_end + buffer > meeting_start):
                quality_score -= 20  # Penalty for lack of buffer

        # Check time of day preferences
        hour = proposed_time.hour

        # Morning focus time (9-11 AM)
        if 9 <= hour < 11:
            quality_score -= 15  # Penalty for using focus time

        # Lunch time (12-1 PM)
        if 12 <= hour < 13:
            quality_score -= 25  # Higher penalty for lunch

        # End of day (after 5 PM)
        if hour >= 17:
            quality_score -= 30  # Penalty for late meetings

        # Check day of week
        day_of_week = proposed_time.weekday()

        # Monday morning (ease into week)
        if day_of_week == 0 and hour < 10:
            quality_score -= 10

        # Friday afternoon (wind down)
        if day_of_week == 4 and hour >= 14:
            quality_score -= 15

        # Check meeting density for that day
        same_day_meetings = [
            m for m in existing_meetings
            if datetime.fromisoformat(m.get("start_time", "")).date() == proposed_time.date()
        ]

        if len(same_day_meetings) > 4:
            quality_score -= 20  # Too many meetings already

        # Apply user preferences if provided
        if user_preferences:
            preferred_hours = user_preferences.get("preferred_meeting_hours", [])
            if preferred_hours and hour not in preferred_hours:
                quality_score -= 15

            avoid_days = user_preferences.get("avoid_days", [])
            if day_of_week in avoid_days:
                quality_score -= 25

        # Calculate final assessment
        quality_score = max(0, quality_score)

        return {
            "quality_score": quality_score,
            "is_available": quality_score > 0,
            "conflict": False,
            "recommendation": self._get_slot_recommendation(quality_score),
            "factors": {
                "time_of_day": "optimal" if 10 <= hour < 12 or 14 <= hour < 16 else "suboptimal",
                "day_of_week": "good" if day_of_week in [1, 2, 3] else "moderate",
                "meeting_density": len(same_day_meetings),
                "has_buffer": quality_score > 80
            }
        }

    def _get_slot_recommendation(self, score: float) -> str:
        """Get recommendation based on quality score"""
        if score >= 80:
            return "Excellent time slot"
        elif score >= 60:
            return "Good time slot"
        elif score >= 40:
            return "Acceptable but not ideal"
        elif score >= 20:
            return "Consider alternative times"
        else:
            return "Poor time slot - find alternative"

    async def suggest_optimal_times(
        self,
        duration_minutes: int,
        existing_meetings: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None,
        num_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal meeting times based on calendar analysis
        """

        suggestions = []
        current_date = datetime.now().date()

        # Define search parameters
        search_days = 7  # Look ahead 7 days
        time_slots = [
            (10, 0),  # 10:00 AM
            (10, 30),  # 10:30 AM
            (14, 0),  # 2:00 PM
            (14, 30),  # 2:30 PM
            (15, 0),  # 3:00 PM
            (11, 0),  # 11:00 AM
            (15, 30),  # 3:30 PM
            (9, 30),  # 9:30 AM
        ]

        # Check each potential slot
        potential_slots = []

        for days_ahead in range(1, search_days + 1):
            check_date = current_date + timedelta(days=days_ahead)

            # Skip weekends
            if check_date.weekday() >= 5:
                continue

            for hour, minute in time_slots:
                proposed_time = datetime.combine(check_date, time(hour, minute))

                # Evaluate slot quality
                quality = await self.get_time_slot_quality(
                    proposed_time,
                    duration_minutes,
                    existing_meetings,
                    constraints
                )

                if quality["is_available"] and quality["quality_score"] > 40:
                    potential_slots.append({
                        "datetime": proposed_time,
                        "quality_score": quality["quality_score"],
                        "recommendation": quality["recommendation"],
                        "factors": quality["factors"]
                    })

        # Sort by quality score and return top suggestions
        potential_slots.sort(key=lambda x: x["quality_score"], reverse=True)

        for slot in potential_slots[:num_suggestions]:
            suggestions.append({
                "proposed_time": slot["datetime"].isoformat(),
                "end_time": (slot["datetime"] + timedelta(minutes=duration_minutes)).isoformat(),
                "quality_score": slot["quality_score"],
                "recommendation": slot["recommendation"],
                "day_name": slot["datetime"].strftime("%A"),
                "time_string": slot["datetime"].strftime("%I:%M %p"),
                "factors": slot["factors"]
            })

        return suggestions