"""
Schedule Optimizer Agent - Intelligent calendar and time management specialist
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, time
import logging
from enum import Enum

from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent, AgentTask, TaskResult
from ..config import AgentConfig

class MeetingType(Enum):
    """Types of meetings"""
    ONE_ON_ONE = "one_on_one"
    TEAM = "team"
    CLIENT = "client"
    PRESENTATION = "presentation"
    BRAINSTORM = "brainstorm"
    REVIEW = "review"
    STANDUP = "standup"

class TimeBlock(BaseModel):
    """Time block structure"""
    start: str = Field(description="Start time")
    end: str = Field(description="End time")
    type: str = Field(description="Block type: focus, meeting, break")
    description: str = Field(description="Block description")
    priority: int = Field(default=5, description="Priority 1-10")
    flexible: bool = Field(default=False, description="Can be rescheduled")

class CalendarEvent(BaseModel):
    """Calendar event structure"""
    title: str = Field(description="Event title")
    start: str = Field(description="Start time")
    end: str = Field(description="End time")
    attendees: List[str] = Field(default_factory=list, description="Attendees")
    location: Optional[str] = Field(default=None, description="Location")
    meeting_type: Optional[MeetingType] = Field(default=None)
    can_optimize: bool = Field(default=True, description="Can be optimized")

class ScheduleOptimizer(BaseAgent):
    """
    Specialized agent for optimizing calendars and managing time efficiently.
    """

    def __init__(self, config: AgentConfig = None, **kwargs):
        config = config or AgentConfig(
            name="ScheduleOptimizer",
            description="Intelligent schedule optimization specialist",
            temperature=0.4,
            max_tokens=2000
        )

        super().__init__(config, **kwargs)

        self.logger = logging.getLogger("delegate.schedule")

        # User preferences
        self.schedule_preferences = self._load_schedule_preferences()

        # Calendar cache
        self.calendar_cache: Dict[str, List[CalendarEvent]] = {}

        # Optimization history
        self.optimization_history: List[Dict[str, Any]] = []

        # Productivity patterns
        self.productivity_patterns = self._load_productivity_patterns()

    def _get_system_prompt(self) -> str:
        """System prompt for schedule optimizer"""
        return """You are an expert schedule optimization specialist responsible for:

1. Analyzing calendars to identify optimization opportunities
2. Suggesting meeting consolidation or elimination
3. Protecting and scheduling focus time blocks
4. Managing calendar conflicts automatically
5. Optimizing meeting schedules for productivity
6. Learning user's time preferences and patterns
7. Balancing work-life boundaries

You work autonomously to continuously optimize the user's schedule,
making intelligent decisions about time allocation and meeting management.

Key principles:
- Protect deep work time blocks
- Minimize context switching
- Batch similar activities together
- Respect energy levels throughout the day
- Maintain work-life balance
- Reduce meeting overload
- Optimize for productivity and well-being"""

    def _get_specialized_tools(self) -> List:
        """Get specialized tools for schedule optimization"""
        tools = []

        # Calendar analysis tool
        tools.append(Tool(
            name="analyze_calendar",
            func=self._analyze_calendar,
            description="Analyze calendar for optimization opportunities"
        ))

        # Meeting optimizer tool
        tools.append(Tool(
            name="optimize_meetings",
            func=self._optimize_meetings,
            description="Optimize meeting schedule"
        ))

        # Focus time tool
        tools.append(Tool(
            name="schedule_focus_time",
            func=self._schedule_focus_time,
            description="Schedule focus time blocks"
        ))

        # Conflict resolution tool
        tools.append(Tool(
            name="resolve_conflicts",
            func=self._resolve_conflicts,
            description="Resolve calendar conflicts"
        ))

        # Time blocking tool
        tools.append(StructuredTool(
            name="create_time_blocks",
            func=self._create_time_blocks,
            description="Create optimized time blocks",
            args_schema=TimeBlock
        ))

        return tools

    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute a schedule optimization task"""
        start_time = datetime.now()

        try:
            task_type = task.parameters.get("optimization_type", "full")

            if task_type == "full_optimization":
                result = await self._handle_full_optimization(task.parameters)
            elif task_type == "meeting_optimization":
                result = await self._handle_meeting_optimization(task.parameters)
            elif task_type == "focus_time":
                result = await self._handle_focus_time_scheduling(task.parameters)
            elif task_type == "conflict_resolution":
                result = await self._handle_conflict_resolution(task.parameters)
            elif task_type == "daily_planning":
                result = await self._handle_daily_planning(task.parameters)
            elif task_type == "workload_balancing":
                result = await self._handle_workload_balancing(task.parameters)
            else:
                raise ValueError(f"Unknown optimization type: {task_type}")

            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="success",
                result=result,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    "optimization_type": task_type,
                    "parameters": task.parameters
                }
            )

        except Exception as e:
            self.logger.error(f"Schedule optimization failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="error",
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    async def _handle_full_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive schedule optimization"""
        self.logger.info("Performing full schedule optimization")

        date_range = parameters.get("date_range", "week")
        calendar_data = await self._fetch_calendar_data(date_range)

        # Analyze current schedule
        analysis = self._analyze_schedule(calendar_data)

        # Identify optimization opportunities
        opportunities = self._identify_opportunities(analysis)

        # Generate optimization plan
        optimization_plan = await self._generate_optimization_plan(
            calendar_data,
            opportunities
        )

        # Apply optimizations
        applied_changes = await self._apply_optimizations(optimization_plan)

        # Calculate improvements
        improvements = self._calculate_improvements(
            analysis,
            applied_changes
        )

        return {
            "analysis": analysis,
            "opportunities": opportunities,
            "optimization_plan": optimization_plan,
            "applied_changes": applied_changes,
            "improvements": improvements,
            "recommendations": self._generate_schedule_recommendations(analysis),
            "next_review": (datetime.now() + timedelta(days=7)).isoformat()
        }

    async def _handle_meeting_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meeting-specific optimization"""
        self.logger.info("Optimizing meetings")

        meetings = parameters.get("meetings", [])
        timeframe = parameters.get("timeframe", "week")

        # Analyze meetings
        meeting_analysis = self._analyze_meetings(meetings)

        # Identify redundant or inefficient meetings
        inefficient_meetings = self._identify_inefficient_meetings(meeting_analysis)

        # Suggest consolidations
        consolidation_suggestions = self._suggest_meeting_consolidations(meetings)

        # Optimize meeting times
        optimized_schedule = await self._optimize_meeting_schedule(meetings)

        # Generate meeting policies
        meeting_policies = self._generate_meeting_policies(meeting_analysis)

        return {
            "meeting_analysis": meeting_analysis,
            "inefficient_meetings": inefficient_meetings,
            "consolidation_suggestions": consolidation_suggestions,
            "optimized_schedule": optimized_schedule,
            "meeting_policies": meeting_policies,
            "time_saved": self._calculate_time_saved(consolidation_suggestions),
            "quality_score": self._calculate_meeting_quality_score(meeting_analysis)
        }

    async def _handle_focus_time_scheduling(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle focus time scheduling"""
        self.logger.info("Scheduling focus time blocks")

        required_hours = parameters.get("required_hours", 4)
        task_type = parameters.get("task_type", "deep_work")
        preferred_times = parameters.get("preferred_times", [])

        # Analyze productivity patterns
        productivity_windows = self._identify_productivity_windows()

        # Find available slots
        available_slots = await self._find_available_slots(
            required_hours,
            productivity_windows
        )

        # Score and rank slots
        ranked_slots = self._rank_focus_slots(
            available_slots,
            task_type,
            preferred_times
        )

        # Create focus blocks
        focus_blocks = self._create_focus_blocks(
            ranked_slots[:3],  # Top 3 options
            task_type
        )

        # Schedule the blocks
        scheduled_blocks = await self._schedule_blocks(focus_blocks)

        return {
            "scheduled_blocks": scheduled_blocks,
            "productivity_windows": productivity_windows,
            "available_options": ranked_slots,
            "total_focus_time": sum(b.get("duration", 0) for b in scheduled_blocks),
            "optimization_notes": self._generate_focus_time_tips(task_type)
        }

    async def _handle_conflict_resolution(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar conflict resolution"""
        self.logger.info("Resolving calendar conflicts")

        conflicts = parameters.get("conflicts", [])

        resolved_conflicts = []

        for conflict in conflicts:
            # Analyze conflict
            conflict_analysis = self._analyze_conflict(conflict)

            # Generate resolution options
            resolution_options = await self._generate_resolution_options(
                conflict,
                conflict_analysis
            )

            # Select best resolution
            best_resolution = self._select_best_resolution(
                resolution_options,
                conflict_analysis
            )

            # Apply resolution
            resolution_result = await self._apply_conflict_resolution(
                conflict,
                best_resolution
            )

            resolved_conflicts.append({
                "conflict": conflict,
                "analysis": conflict_analysis,
                "resolution": best_resolution,
                "result": resolution_result
            })

        return {
            "resolved_conflicts": resolved_conflicts,
            "total_conflicts": len(conflicts),
            "successfully_resolved": len([r for r in resolved_conflicts
                                         if r["result"].get("success")]),
            "recommendations": self._generate_conflict_prevention_tips()
        }

    async def _handle_daily_planning(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle daily schedule planning"""
        self.logger.info("Planning daily schedule")

        date = parameters.get("date", datetime.now().date().isoformat())
        priorities = parameters.get("priorities", [])
        energy_level = parameters.get("energy_level", "normal")

        # Get day's events
        daily_events = await self._get_daily_events(date)

        # Analyze day structure
        day_analysis = self._analyze_day_structure(daily_events)

        # Create optimal daily plan
        daily_plan = self._create_daily_plan(
            daily_events,
            priorities,
            energy_level
        )

        # Add buffer time
        buffered_plan = self._add_buffer_time(daily_plan)

        # Generate time-boxed schedule
        time_boxed_schedule = self._create_time_boxed_schedule(buffered_plan)

        # Create daily tips
        daily_tips = self._generate_daily_tips(day_analysis, energy_level)

        return {
            "date": date,
            "daily_plan": time_boxed_schedule,
            "priorities_addressed": self._check_priorities_coverage(
                time_boxed_schedule,
                priorities
            ),
            "energy_optimization": self._optimize_for_energy(
                time_boxed_schedule,
                energy_level
            ),
            "daily_tips": daily_tips,
            "flexibility_score": self._calculate_flexibility_score(time_boxed_schedule),
            "projected_productivity": self._estimate_daily_productivity(time_boxed_schedule)
        }

    async def _handle_workload_balancing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workload balancing across time periods"""
        self.logger.info("Balancing workload")

        timeframe = parameters.get("timeframe", "week")
        target_hours = parameters.get("target_hours", 40)

        # Analyze current workload
        workload_analysis = await self._analyze_workload(timeframe)

        # Identify imbalances
        imbalances = self._identify_workload_imbalances(
            workload_analysis,
            target_hours
        )

        # Generate rebalancing plan
        rebalancing_plan = self._generate_rebalancing_plan(
            workload_analysis,
            imbalances,
            target_hours
        )

        # Apply rebalancing
        rebalancing_results = await self._apply_rebalancing(rebalancing_plan)

        # Calculate work-life balance score
        balance_score = self._calculate_work_life_balance(rebalancing_results)

        return {
            "workload_analysis": workload_analysis,
            "imbalances": imbalances,
            "rebalancing_plan": rebalancing_plan,
            "results": rebalancing_results,
            "balance_score": balance_score,
            "sustainability_rating": self._assess_schedule_sustainability(
                rebalancing_results
            ),
            "recommendations": self._generate_balance_recommendations(balance_score)
        }

    # Helper methods

    def _analyze_calendar(self, context: str) -> str:
        """Tool function for calendar analysis"""
        return f"Calendar analyzed: {context}"

    def _optimize_meetings(self, context: str) -> str:
        """Tool function for meeting optimization"""
        return f"Meetings optimized: {context}"

    def _schedule_focus_time(self, context: str) -> str:
        """Tool function for focus time scheduling"""
        return f"Focus time scheduled: {context}"

    def _resolve_conflicts(self, context: str) -> str:
        """Tool function for conflict resolution"""
        return f"Conflicts resolved: {context}"

    def _create_time_blocks(self, block: TimeBlock) -> Dict[str, Any]:
        """Tool function for creating time blocks"""
        return {
            "block_id": f"block_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created": True
        }

    def _load_schedule_preferences(self) -> Dict[str, Any]:
        """Load user's schedule preferences"""
        return {
            "work_hours": {"start": "09:00", "end": "18:00"},
            "preferred_meeting_times": ["10:00-12:00", "14:00-16:00"],
            "focus_time_preference": "morning",
            "meeting_duration_preference": 30,
            "buffer_time": 15,
            "lunch_time": {"start": "12:00", "end": "13:00"},
            "no_meeting_days": [],
            "max_meetings_per_day": 4
        }

    def _load_productivity_patterns(self) -> Dict[str, Any]:
        """Load user's productivity patterns"""
        return {
            "peak_hours": ["09:00-11:00", "14:00-16:00"],
            "low_energy_times": ["13:00-14:00", "16:00-17:00"],
            "best_focus_days": ["Tuesday", "Thursday"],
            "meeting_fatigue_threshold": 3,
            "context_switch_penalty": 15  # minutes
        }

    async def _fetch_calendar_data(self, date_range: str) -> List[CalendarEvent]:
        """Fetch calendar data for analysis"""
        # Would integrate with calendar API
        return [
            CalendarEvent(
                title="Team Meeting",
                start=(datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                end=(datetime.now() + timedelta(days=1, hours=11)).isoformat(),
                attendees=["team"],
                meeting_type=MeetingType.TEAM
            ),
            CalendarEvent(
                title="Client Call",
                start=(datetime.now() + timedelta(days=2, hours=14)).isoformat(),
                end=(datetime.now() + timedelta(days=2, hours=15)).isoformat(),
                attendees=["client"],
                meeting_type=MeetingType.CLIENT
            )
        ]

    def _analyze_schedule(self, calendar_data: List[CalendarEvent]) -> Dict[str, Any]:
        """Analyze schedule for patterns and issues"""
        analysis = {
            "total_events": len(calendar_data),
            "meeting_hours": 0,
            "focus_time_available": 0,
            "fragmentation_score": 0,
            "meeting_distribution": {},
            "time_utilization": 0
        }

        # Calculate meeting hours
        for event in calendar_data:
            start = datetime.fromisoformat(event.start)
            end = datetime.fromisoformat(event.end)
            duration = (end - start).total_seconds() / 3600
            analysis["meeting_hours"] += duration

        # Calculate available focus time
        work_hours_per_day = 8
        total_work_hours = work_hours_per_day * 5  # Assuming work week
        analysis["focus_time_available"] = total_work_hours - analysis["meeting_hours"]

        # Calculate fragmentation
        analysis["fragmentation_score"] = self._calculate_fragmentation(calendar_data)

        # Time utilization
        analysis["time_utilization"] = (analysis["meeting_hours"] / total_work_hours) * 100

        return analysis

    def _calculate_fragmentation(self, events: List[CalendarEvent]) -> float:
        """Calculate schedule fragmentation score"""
        if len(events) < 2:
            return 0.0

        # Sort events by start time
        sorted_events = sorted(events, key=lambda e: e.start)

        gaps = []
        for i in range(len(sorted_events) - 1):
            end = datetime.fromisoformat(sorted_events[i].end)
            start = datetime.fromisoformat(sorted_events[i + 1].start)
            gap = (start - end).total_seconds() / 60  # Gap in minutes

            if 0 < gap < 60:  # Gaps less than an hour cause fragmentation
                gaps.append(gap)

        # Higher score means more fragmentation
        if not gaps:
            return 0.0

        avg_gap = sum(gaps) / len(gaps)
        fragmentation = (60 - avg_gap) / 60  # Normalize to 0-1

        return fragmentation

    def _identify_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify schedule optimization opportunities"""
        opportunities = []

        # Check for excessive meetings
        if analysis["meeting_hours"] > 20:
            opportunities.append({
                "type": "meeting_reduction",
                "description": "Excessive meeting load detected",
                "potential_time_saved": analysis["meeting_hours"] * 0.2,
                "priority": "high"
            })

        # Check for fragmentation
        if analysis["fragmentation_score"] > 0.5:
            opportunities.append({
                "type": "consolidation",
                "description": "Schedule is highly fragmented",
                "potential_improvement": "30% better focus time",
                "priority": "medium"
            })

        # Check for focus time
        if analysis["focus_time_available"] < 12:
            opportunities.append({
                "type": "focus_time",
                "description": "Insufficient focus time available",
                "recommendation": "Block 2-hour focus sessions",
                "priority": "high"
            })

        return opportunities

    async def _generate_optimization_plan(
        self,
        calendar_data: List[CalendarEvent],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive optimization plan"""
        plan = {
            "actions": [],
            "timeline": [],
            "expected_improvements": {}
        }

        for opportunity in opportunities:
            if opportunity["type"] == "meeting_reduction":
                plan["actions"].append({
                    "action": "reduce_meetings",
                    "target": "20% reduction",
                    "method": "Consolidate similar meetings"
                })

            elif opportunity["type"] == "consolidation":
                plan["actions"].append({
                    "action": "consolidate_schedule",
                    "target": "Batch meetings together",
                    "method": "Group by type and day"
                })

            elif opportunity["type"] == "focus_time":
                plan["actions"].append({
                    "action": "block_focus_time",
                    "target": "4 hours daily",
                    "method": "Morning blocks when possible"
                })

        return plan

    async def _apply_optimizations(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply optimization plan to calendar"""
        changes = []

        for action in plan.get("actions", []):
            # Would apply actual calendar changes
            changes.append({
                "action": action["action"],
                "status": "applied",
                "result": f"{action['target']} achieved"
            })

        return changes

    def _calculate_improvements(
        self,
        before: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate improvements from optimization"""
        return {
            "time_saved": len(changes) * 2,  # Hours saved
            "fragmentation_reduced": 25,  # Percentage
            "focus_time_increased": 40,  # Percentage
            "meeting_efficiency": 30  # Percentage improvement
        }

    def _generate_schedule_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate schedule recommendations"""
        recommendations = []

        if analysis["meeting_hours"] > 20:
            recommendations.append("Consider declining non-essential meetings")

        if analysis["fragmentation_score"] > 0.5:
            recommendations.append("Batch similar activities together")

        if analysis["focus_time_available"] < 12:
            recommendations.append("Block calendar for deep work sessions")

        recommendations.append("Review and eliminate recurring meetings quarterly")
        recommendations.append("Implement 'No Meeting Friday' policy")

        return recommendations

    def _analyze_meetings(self, meetings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze meetings for optimization"""
        return {
            "total_meetings": len(meetings),
            "total_time": sum(m.get("duration", 30) for m in meetings),
            "average_duration": sum(m.get("duration", 30) for m in meetings) / len(meetings) if meetings else 0,
            "meeting_types": self._categorize_meetings(meetings),
            "attendance_patterns": self._analyze_attendance(meetings)
        }

    def _categorize_meetings(self, meetings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize meetings by type"""
        categories = {}
        for meeting in meetings:
            meeting_type = meeting.get("type", "general")
            categories[meeting_type] = categories.get(meeting_type, 0) + 1
        return categories

    def _analyze_attendance(self, meetings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze meeting attendance patterns"""
        return {
            "average_attendees": 5,
            "large_meetings": len([m for m in meetings if len(m.get("attendees", [])) > 8]),
            "one_on_ones": len([m for m in meetings if len(m.get("attendees", [])) == 2])
        }

    def _identify_inefficient_meetings(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify inefficient meetings"""
        inefficient = []

        # Meetings that are too long
        if analysis["average_duration"] > 45:
            inefficient.append({
                "issue": "meetings_too_long",
                "recommendation": "Default to 30-minute meetings"
            })

        # Too many large meetings
        if analysis["attendance_patterns"]["large_meetings"] > 5:
            inefficient.append({
                "issue": "too_many_large_meetings",
                "recommendation": "Replace with async updates where possible"
            })

        return inefficient

    def _suggest_meeting_consolidations(self, meetings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest meeting consolidations"""
        consolidations = []

        # Group similar meetings
        meeting_groups = {}
        for meeting in meetings:
            key = meeting.get("type", "general")
            if key not in meeting_groups:
                meeting_groups[key] = []
            meeting_groups[key].append(meeting)

        for meeting_type, group in meeting_groups.items():
            if len(group) > 2:
                consolidations.append({
                    "type": meeting_type,
                    "current_meetings": len(group),
                    "suggested_meetings": 1,
                    "time_saved": (len(group) - 1) * 30  # minutes
                })

        return consolidations

    async def _optimize_meeting_schedule(self, meetings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize meeting schedule"""
        optimized = []

        # Sort meetings by priority and group by day
        for meeting in meetings:
            optimized_meeting = meeting.copy()

            # Suggest optimal time based on meeting type
            if meeting.get("type") == "brainstorm":
                optimized_meeting["suggested_time"] = "morning"
            elif meeting.get("type") == "review":
                optimized_meeting["suggested_time"] = "end_of_day"

            optimized.append(optimized_meeting)

        return optimized

    def _generate_meeting_policies(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate meeting policies based on analysis"""
        policies = []

        if analysis["average_duration"] > 30:
            policies.append("Default meeting duration: 30 minutes")

        if analysis["total_meetings"] > 15:
            policies.append("Meeting-free time blocks: 9-10am daily")

        policies.append("Require agenda for meetings > 30 minutes")
        policies.append("Limit recurring meetings to monthly review")

        return policies

    def _calculate_time_saved(self, consolidations: List[Dict[str, Any]]) -> int:
        """Calculate total time saved from consolidations"""
        return sum(c.get("time_saved", 0) for c in consolidations)

    def _calculate_meeting_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate meeting quality score"""
        score = 100.0

        # Penalize for too many meetings
        if analysis["total_meetings"] > 15:
            score -= 20

        # Penalize for long average duration
        if analysis["average_duration"] > 45:
            score -= 15

        # Bonus for good distribution
        if analysis.get("meeting_types", {}).get("one_on_one", 0) > 3:
            score += 10

        return max(0, min(100, score))

    def _identify_productivity_windows(self) -> List[Dict[str, Any]]:
        """Identify optimal productivity windows"""
        return [
            {"start": "09:00", "end": "11:00", "quality": "peak"},
            {"start": "14:00", "end": "16:00", "quality": "good"},
            {"start": "16:00", "end": "17:00", "quality": "moderate"}
        ]

    async def _find_available_slots(
        self,
        required_hours: int,
        productivity_windows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find available time slots"""
        slots = []

        for window in productivity_windows:
            # Check calendar for availability
            slots.append({
                "start": window["start"],
                "duration": min(required_hours, 2),
                "quality": window["quality"],
                "date": (datetime.now() + timedelta(days=1)).date().isoformat()
            })

        return slots

    def _rank_focus_slots(
        self,
        slots: List[Dict[str, Any]],
        task_type: str,
        preferred_times: List[str]
    ) -> List[Dict[str, Any]]:
        """Rank focus time slots by quality"""
        ranked = []

        for slot in slots:
            score = 0

            # Score based on quality
            if slot["quality"] == "peak":
                score += 10
            elif slot["quality"] == "good":
                score += 7
            else:
                score += 5

            # Score based on task type match
            if task_type == "deep_work" and slot["quality"] == "peak":
                score += 5

            # Score based on preference match
            if slot["start"] in preferred_times:
                score += 3

            slot["score"] = score
            ranked.append(slot)

        return sorted(ranked, key=lambda x: x["score"], reverse=True)

    def _create_focus_blocks(
        self,
        slots: List[Dict[str, Any]],
        task_type: str
    ) -> List[Dict[str, Any]]:
        """Create focus time blocks"""
        blocks = []

        for slot in slots:
            blocks.append({
                "type": "focus",
                "task_type": task_type,
                "start": slot["start"],
                "duration": slot["duration"],
                "date": slot["date"],
                "protected": True
            })

        return blocks

    async def _schedule_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Schedule blocks in calendar"""
        scheduled = []

        for block in blocks:
            # Would actually create calendar events
            scheduled.append({
                **block,
                "scheduled": True,
                "calendar_id": f"focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            })

        return scheduled

    def _generate_focus_time_tips(self, task_type: str) -> List[str]:
        """Generate tips for focus time"""
        tips = [
            "Turn off notifications during focus blocks",
            "Use time-boxing technique for better productivity",
            "Take 5-minute breaks every 25 minutes"
        ]

        if task_type == "deep_work":
            tips.append("Prepare materials the night before")
            tips.append("Start with the most challenging task")

        return tips

    def _analyze_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a calendar conflict"""
        return {
            "type": conflict.get("type", "overlap"),
            "severity": "high" if conflict.get("attendees", 0) > 5 else "medium",
            "flexibility": self._assess_flexibility(conflict)
        }

    def _assess_flexibility(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Assess flexibility of conflicting events"""
        return {
            "event1_flexible": True,
            "event2_flexible": False,
            "can_delegate": False
        }

    async def _generate_resolution_options(
        self,
        conflict: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate options for resolving conflict"""
        options = []

        # Reschedule option
        options.append({
            "type": "reschedule",
            "action": "Move less important meeting",
            "impact": "minimal"
        })

        # Delegate option
        if analysis["flexibility"]["can_delegate"]:
            options.append({
                "type": "delegate",
                "action": "Send delegate to one meeting",
                "impact": "low"
            })

        # Split attendance option
        options.append({
            "type": "split",
            "action": "Attend part of each meeting",
            "impact": "medium"
        })

        return options

    def _select_best_resolution(
        self,
        options: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select best resolution option"""
        # Simple selection - would be more sophisticated
        for option in options:
            if option["impact"] == "minimal":
                return option

        return options[0] if options else {"type": "none", "action": "No resolution available"}

    async def _apply_conflict_resolution(
        self,
        conflict: Dict[str, Any],
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply selected resolution"""
        # Would actually modify calendar
        return {
            "success": True,
            "resolution_applied": resolution["type"],
            "updated_events": []
        }

    def _generate_conflict_prevention_tips(self) -> List[str]:
        """Generate tips for preventing conflicts"""
        return [
            "Block buffer time between meetings",
            "Use scheduling links with availability",
            "Review calendar weekly for potential conflicts",
            "Set meeting response deadlines"
        ]

    async def _get_daily_events(self, date: str) -> List[CalendarEvent]:
        """Get events for a specific day"""
        # Would fetch from calendar API
        return []

    def _analyze_day_structure(self, events: List[CalendarEvent]) -> Dict[str, Any]:
        """Analyze structure of a day"""
        return {
            "meeting_density": len(events),
            "focus_blocks": 0,
            "break_time": 60,  # minutes
            "energy_demand": "moderate"
        }

    def _create_daily_plan(
        self,
        events: List[CalendarEvent],
        priorities: List[str],
        energy_level: str
    ) -> List[Dict[str, Any]]:
        """Create optimized daily plan"""
        plan = []

        # Add existing events
        for event in events:
            plan.append({
                "time": event.start,
                "activity": event.title,
                "type": "meeting",
                "energy_required": "high"
            })

        # Add priority tasks
        for priority in priorities:
            plan.append({
                "time": "TBD",
                "activity": priority,
                "type": "task",
                "energy_required": "medium"
            })

        return plan

    def _add_buffer_time(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add buffer time between activities"""
        buffered = []

        for i, item in enumerate(plan):
            buffered.append(item)

            if i < len(plan) - 1:
                buffered.append({
                    "time": "buffer",
                    "activity": "Transition/Break",
                    "type": "break",
                    "duration": 15
                })

        return buffered

    def _create_time_boxed_schedule(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create time-boxed schedule"""
        schedule = []
        current_time = datetime.strptime("09:00", "%H:%M")

        for item in plan:
            duration = item.get("duration", 30)
            schedule.append({
                **item,
                "start": current_time.strftime("%H:%M"),
                "end": (current_time + timedelta(minutes=duration)).strftime("%H:%M")
            })
            current_time += timedelta(minutes=duration)

        return schedule

    def _check_priorities_coverage(
        self,
        schedule: List[Dict[str, Any]],
        priorities: List[str]
    ) -> Dict[str, bool]:
        """Check if priorities are covered in schedule"""
        coverage = {}
        scheduled_activities = [s["activity"] for s in schedule]

        for priority in priorities:
            coverage[priority] = priority in scheduled_activities

        return coverage

    def _optimize_for_energy(
        self,
        schedule: List[Dict[str, Any]],
        energy_level: str
    ) -> List[Dict[str, Any]]:
        """Optimize schedule for energy level"""
        if energy_level == "low":
            # Move high-energy tasks to optimal times
            for item in schedule:
                if item.get("energy_required") == "high":
                    item["recommended_time"] = "morning"

        return schedule

    def _generate_daily_tips(self, analysis: Dict[str, Any], energy_level: str) -> List[str]:
        """Generate daily schedule tips"""
        tips = []

        if analysis["meeting_density"] > 4:
            tips.append("High meeting load - protect remaining focus time")

        if energy_level == "low":
            tips.append("Schedule important tasks for peak energy times")
            tips.append("Take regular breaks to maintain energy")

        tips.append("Review and adjust schedule mid-day if needed")

        return tips

    def _calculate_flexibility_score(self, schedule: List[Dict[str, Any]]) -> float:
        """Calculate schedule flexibility score"""
        total_time = len(schedule) * 30  # Average 30 min per item
        buffer_time = len([s for s in schedule if s.get("type") == "break"]) * 15

        return (buffer_time / total_time * 100) if total_time > 0 else 0

    def _estimate_daily_productivity(self, schedule: List[Dict[str, Any]]) -> float:
        """Estimate daily productivity score"""
        focus_time = len([s for s in schedule if s.get("type") in ["task", "focus"]])
        meeting_time = len([s for s in schedule if s.get("type") == "meeting")])

        if focus_time + meeting_time == 0:
            return 0

        return (focus_time / (focus_time + meeting_time)) * 100

    async def _analyze_workload(self, timeframe: str) -> Dict[str, Any]:
        """Analyze workload over timeframe"""
        return {
            "total_hours": 45,
            "distribution": {
                "Monday": 10,
                "Tuesday": 9,
                "Wednesday": 11,
                "Thursday": 8,
                "Friday": 7
            },
            "peak_days": ["Monday", "Wednesday"],
            "light_days": ["Friday"]
        }

    def _identify_workload_imbalances(
        self,
        analysis: Dict[str, Any],
        target_hours: int
    ) -> List[Dict[str, Any]]:
        """Identify workload imbalances"""
        imbalances = []
        daily_target = target_hours / 5

        for day, hours in analysis["distribution"].items():
            if hours > daily_target * 1.2:
                imbalances.append({
                    "day": day,
                    "issue": "overloaded",
                    "hours": hours,
                    "excess": hours - daily_target
                })
            elif hours < daily_target * 0.8:
                imbalances.append({
                    "day": day,
                    "issue": "underutilized",
                    "hours": hours,
                    "deficit": daily_target - hours
                })

        return imbalances

    def _generate_rebalancing_plan(
        self,
        analysis: Dict[str, Any],
        imbalances: List[Dict[str, Any]],
        target_hours: int
    ) -> Dict[str, Any]:
        """Generate workload rebalancing plan"""
        plan = {
            "moves": [],
            "target_distribution": {}
        }

        daily_target = target_hours / 5

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            plan["target_distribution"][day] = daily_target

        # Generate moves to balance workload
        for imbalance in imbalances:
            if imbalance["issue"] == "overloaded":
                plan["moves"].append({
                    "from": imbalance["day"],
                    "to": analysis["light_days"][0] if analysis["light_days"] else "Friday",
                    "hours": imbalance["excess"]
                })

        return plan

    async def _apply_rebalancing(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply workload rebalancing"""
        # Would actually move calendar events
        return {
            "moves_completed": len(plan["moves"]),
            "new_distribution": plan["target_distribution"],
            "success": True
        }

    def _calculate_work_life_balance(self, results: Dict[str, Any]) -> float:
        """Calculate work-life balance score"""
        distribution = results.get("new_distribution", {})

        # Check for reasonable daily hours
        score = 100.0
        for day, hours in distribution.items():
            if hours > 9:
                score -= 10
            if hours > 10:
                score -= 20

        return max(0, score)

    def _assess_schedule_sustainability(self, results: Dict[str, Any]) -> str:
        """Assess sustainability of schedule"""
        distribution = results.get("new_distribution", {})
        max_daily = max(distribution.values()) if distribution else 0

        if max_daily <= 8:
            return "sustainable"
        elif max_daily <= 9:
            return "moderate"
        else:
            return "unsustainable"

    def _generate_balance_recommendations(self, score: float) -> List[str]:
        """Generate work-life balance recommendations"""
        recommendations = []

        if score < 70:
            recommendations.append("Consider delegating or declining some commitments")
            recommendations.append("Protect personal time by setting firm boundaries")

        if score < 50:
            recommendations.append("Schedule is unsustainable - immediate reduction needed")

        recommendations.append("Build in recovery time between intense work periods")
        recommendations.append("Maintain at least one meeting-free day per week")

        return recommendations