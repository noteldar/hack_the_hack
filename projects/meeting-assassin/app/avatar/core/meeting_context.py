"""
Meeting Context Management - Tracks meeting state and context
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class MeetingType(Enum):
    """Types of meetings"""
    STANDUP = "standup"
    PLANNING = "planning"
    REVIEW = "review"
    ONE_ON_ONE = "one_on_one"
    ALL_HANDS = "all_hands"
    BRAINSTORM = "brainstorm"
    DECISION = "decision"
    PRESENTATION = "presentation"
    INTERVIEW = "interview"
    CLIENT = "client"
    TRAINING = "training"
    RETROSPECTIVE = "retrospective"


class MeetingPriority(Enum):
    """Meeting priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MeetingAgenda:
    """Meeting agenda structure"""
    items: List[Dict[str, Any]] = field(default_factory=list)
    time_allocated: Dict[str, int] = field(default_factory=dict)  # minutes per item
    current_item: Optional[str] = None
    completed_items: List[str] = field(default_factory=list)


@dataclass
class MeetingContext:
    """Complete meeting context and metadata"""
    # Basic info
    meeting_id: str
    title: str
    meeting_type: MeetingType
    priority: MeetingPriority = MeetingPriority.MEDIUM

    # Time info
    scheduled_start: datetime = field(default_factory=datetime.now)
    scheduled_duration: int = 30  # minutes
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None

    # Participants
    organizer: str = ""
    required_attendees: List[str] = field(default_factory=list)
    optional_attendees: List[str] = field(default_factory=list)
    actual_attendees: List[str] = field(default_factory=list)

    # Meeting details
    description: str = ""
    agenda: MeetingAgenda = field(default_factory=MeetingAgenda)
    goals: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)

    # Context and preparation
    background_docs: List[str] = field(default_factory=list)
    previous_meeting_ref: Optional[str] = None
    pre_read_materials: List[str] = field(default_factory=list)

    # Platform info
    platform: str = "zoom"  # zoom, teams, meet, etc.
    meeting_url: Optional[str] = None
    meeting_password: Optional[str] = None
    recording_enabled: bool = True

    # AI participation settings
    ai_participation_level: str = "active"  # active, passive, selective
    auto_respond: bool = True
    take_notes: bool = True
    generate_summary: bool = True
    extract_actions: bool = True

    # Custom context
    custom_context: Dict[str, Any] = field(default_factory=dict)
    keywords_to_watch: List[str] = field(default_factory=list)
    decisions_needed: List[str] = field(default_factory=list)


class MeetingContextManager:
    """Manages meeting context throughout the meeting lifecycle"""

    def __init__(self):
        self.contexts: Dict[str, MeetingContext] = {}
        self.active_meeting: Optional[MeetingContext] = None

    def create_context(self, **kwargs) -> MeetingContext:
        """Create a new meeting context"""
        context = MeetingContext(**kwargs)
        self.contexts[context.meeting_id] = context
        return context

    def get_context(self, meeting_id: str) -> Optional[MeetingContext]:
        """Retrieve meeting context by ID"""
        return self.contexts.get(meeting_id)

    def set_active(self, meeting_id: str) -> bool:
        """Set the active meeting"""
        context = self.get_context(meeting_id)
        if context:
            self.active_meeting = context
            context.actual_start = datetime.now()
            return True
        return False

    def end_meeting(self, meeting_id: str) -> Optional[MeetingContext]:
        """End a meeting and update context"""
        context = self.get_context(meeting_id)
        if context:
            context.actual_end = datetime.now()
            if self.active_meeting and self.active_meeting.meeting_id == meeting_id:
                self.active_meeting = None
            return context
        return None

    def update_agenda_progress(self, meeting_id: str, completed_item: str) -> bool:
        """Update agenda progress"""
        context = self.get_context(meeting_id)
        if context and context.agenda:
            if completed_item not in context.agenda.completed_items:
                context.agenda.completed_items.append(completed_item)

            # Move to next item
            items = [item['title'] for item in context.agenda.items
                    if item['title'] not in context.agenda.completed_items]
            if items:
                context.agenda.current_item = items[0]
            else:
                context.agenda.current_item = None
            return True
        return False

    def add_attendee(self, meeting_id: str, attendee: str) -> bool:
        """Add an attendee to the meeting"""
        context = self.get_context(meeting_id)
        if context and attendee not in context.actual_attendees:
            context.actual_attendees.append(attendee)
            return True
        return False

    def get_meeting_progress(self, meeting_id: str) -> Dict[str, Any]:
        """Get current meeting progress"""
        context = self.get_context(meeting_id)
        if not context:
            return {}

        elapsed_time = 0
        if context.actual_start:
            elapsed_time = (datetime.now() - context.actual_start).total_seconds() / 60

        total_agenda_items = len(context.agenda.items) if context.agenda else 0
        completed_items = len(context.agenda.completed_items) if context.agenda else 0

        return {
            "elapsed_minutes": round(elapsed_time, 1),
            "scheduled_duration": context.scheduled_duration,
            "progress_percentage": round((elapsed_time / context.scheduled_duration) * 100, 1)
                                 if context.scheduled_duration > 0 else 0,
            "agenda_progress": {
                "total": total_agenda_items,
                "completed": completed_items,
                "current": context.agenda.current_item if context.agenda else None,
                "percentage": round((completed_items / total_agenda_items) * 100, 1)
                            if total_agenda_items > 0 else 0
            },
            "attendee_count": len(context.actual_attendees),
            "is_overtime": elapsed_time > context.scheduled_duration
        }

    def get_context_prompt(self, meeting_id: str) -> str:
        """Generate context prompt for AI"""
        context = self.get_context(meeting_id)
        if not context:
            return ""

        prompt = f"""
Meeting Context:
- Title: {context.title}
- Type: {context.meeting_type.value}
- Priority: {context.priority.value}
- Organizer: {context.organizer}
- Duration: {context.scheduled_duration} minutes
"""
        if context.goals:
            prompt += f"- Goals: {', '.join(context.goals[:3])}\n"

        if context.expected_outcomes:
            prompt += f"- Expected Outcomes: {', '.join(context.expected_outcomes[:3])}\n"

        if context.agenda and context.agenda.items:
            agenda_items = [item.get('title', '') for item in context.agenda.items[:5]]
            prompt += f"- Agenda: {', '.join(agenda_items)}\n"

        if context.decisions_needed:
            prompt += f"- Decisions Needed: {', '.join(context.decisions_needed[:3])}\n"

        if context.keywords_to_watch:
            prompt += f"- Important Topics: {', '.join(context.keywords_to_watch[:5])}\n"

        return prompt

    def should_ai_participate(self, meeting_id: str, current_topic: str = "") -> bool:
        """Determine if AI should participate based on context"""
        context = self.get_context(meeting_id)
        if not context:
            return False

        # Always participate in high priority meetings
        if context.priority == MeetingPriority.CRITICAL:
            return True

        # Check participation level
        if context.ai_participation_level == "passive":
            return False
        elif context.ai_participation_level == "selective":
            # Check if current topic matches keywords
            if current_topic and context.keywords_to_watch:
                return any(keyword.lower() in current_topic.lower()
                          for keyword in context.keywords_to_watch)
            return False

        return context.auto_respond

    def to_dict(self, meeting_id: str) -> Dict[str, Any]:
        """Convert context to dictionary"""
        context = self.get_context(meeting_id)
        if not context:
            return {}

        return {
            "meeting_id": context.meeting_id,
            "title": context.title,
            "type": context.meeting_type.value,
            "priority": context.priority.value,
            "scheduled_start": context.scheduled_start.isoformat(),
            "duration": context.scheduled_duration,
            "organizer": context.organizer,
            "attendees": {
                "required": context.required_attendees,
                "optional": context.optional_attendees,
                "actual": context.actual_attendees
            },
            "agenda": {
                "items": context.agenda.items if context.agenda else [],
                "current": context.agenda.current_item if context.agenda else None,
                "completed": context.agenda.completed_items if context.agenda else []
            },
            "goals": context.goals,
            "expected_outcomes": context.expected_outcomes,
            "ai_settings": {
                "participation": context.ai_participation_level,
                "auto_respond": context.auto_respond,
                "take_notes": context.take_notes,
                "generate_summary": context.generate_summary
            },
            "progress": self.get_meeting_progress(meeting_id)
        }


# Meeting templates for common scenarios
class MeetingTemplates:
    @staticmethod
    def daily_standup() -> Dict[str, Any]:
        """Template for daily standup meetings"""
        return {
            "meeting_type": MeetingType.STANDUP,
            "scheduled_duration": 15,
            "agenda": MeetingAgenda(
                items=[
                    {"title": "Yesterday's progress", "duration": 5},
                    {"title": "Today's plan", "duration": 5},
                    {"title": "Blockers", "duration": 5}
                ]
            ),
            "ai_participation_level": "selective",
            "keywords_to_watch": ["blocker", "help", "issue", "problem"]
        }

    @staticmethod
    def sprint_planning() -> Dict[str, Any]:
        """Template for sprint planning meetings"""
        return {
            "meeting_type": MeetingType.PLANNING,
            "scheduled_duration": 120,
            "agenda": MeetingAgenda(
                items=[
                    {"title": "Sprint goal definition", "duration": 15},
                    {"title": "Backlog refinement", "duration": 30},
                    {"title": "Story estimation", "duration": 45},
                    {"title": "Sprint commitment", "duration": 20},
                    {"title": "Risk assessment", "duration": 10}
                ]
            ),
            "ai_participation_level": "active",
            "keywords_to_watch": ["estimate", "risk", "dependency", "commitment", "capacity"]
        }

    @staticmethod
    def client_meeting() -> Dict[str, Any]:
        """Template for client meetings"""
        return {
            "meeting_type": MeetingType.CLIENT,
            "scheduled_duration": 60,
            "priority": MeetingPriority.HIGH,
            "ai_participation_level": "active",
            "auto_respond": True,
            "keywords_to_watch": ["requirement", "deadline", "budget", "deliverable", "timeline"]
        }

    @staticmethod
    def one_on_one() -> Dict[str, Any]:
        """Template for one-on-one meetings"""
        return {
            "meeting_type": MeetingType.ONE_ON_ONE,
            "scheduled_duration": 30,
            "ai_participation_level": "passive",
            "auto_respond": False,
            "take_notes": True,
            "generate_summary": True
        }