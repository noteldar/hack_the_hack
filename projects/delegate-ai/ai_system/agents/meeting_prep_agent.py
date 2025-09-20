"""
Meeting Preparation Agent - Autonomous meeting preparation specialist
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent, AgentTask, TaskResult
from ..config import AgentConfig

class MeetingInfo(BaseModel):
    """Meeting information structure"""
    title: str = Field(description="Meeting title")
    attendees: List[str] = Field(description="List of attendee names")
    date: str = Field(description="Meeting date")
    time: str = Field(description="Meeting time")
    duration: int = Field(description="Duration in minutes")
    topic: Optional[str] = Field(description="Meeting topic or agenda")

class AttendeeResearch(BaseModel):
    """Research results for an attendee"""
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    background: Optional[str] = None
    recent_activity: Optional[str] = None
    common_interests: List[str] = Field(default_factory=list)
    talking_points: List[str] = Field(default_factory=list)

class MeetingPrepAgent(BaseAgent):
    """
    Specialized agent for autonomous meeting preparation.
    Researches attendees, prepares agendas, and creates briefing documents.
    """

    def __init__(self, config: AgentConfig = None, **kwargs):
        # Initialize with specific configuration
        config = config or AgentConfig(
            name="MeetingPrepAgent",
            description="Autonomous meeting preparation specialist",
            temperature=0.6,
            max_tokens=3000
        )

        super().__init__(config, **kwargs)

        self.logger = logging.getLogger("delegate.meeting_prep")

        # Meeting preparation templates
        self.agenda_templates = self._load_agenda_templates()
        self.briefing_template = self._load_briefing_template()

        # Research cache
        self.research_cache: Dict[str, AttendeeResearch] = {}

    def _get_system_prompt(self) -> str:
        """System prompt for meeting preparation agent"""
        return """You are an expert meeting preparation specialist. Your role is to:

1. Research meeting attendees to understand their background and interests
2. Generate comprehensive meeting agendas based on context and goals
3. Prepare detailed briefing documents with key talking points
4. Identify potential discussion topics and outcomes
5. Provide strategic recommendations for meeting success

You work autonomously and proactively, preparing meetings before they occur.
You have access to web search and other tools to gather information.

Always provide thorough, actionable preparation materials that help the user
have successful, productive meetings."""

    def _get_specialized_tools(self) -> List:
        """Get specialized tools for meeting preparation"""
        tools = []

        # Web search tool for research
        search_tool = DuckDuckGoSearchRun()
        tools.append(Tool(
            name="web_search",
            func=search_tool.run,
            description="Search the web for information about people, companies, and topics"
        ))

        # LinkedIn research tool (simulated)
        tools.append(StructuredTool(
            name="linkedin_research",
            func=self._linkedin_research,
            description="Research professional background on LinkedIn",
            args_schema=AttendeeResearch
        ))

        # Agenda generator tool
        tools.append(Tool(
            name="generate_agenda",
            func=self._generate_agenda,
            description="Generate a meeting agenda based on context"
        ))

        # Talking points generator
        tools.append(Tool(
            name="generate_talking_points",
            func=self._generate_talking_points,
            description="Generate key talking points for the meeting"
        ))

        return tools

    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute a meeting preparation task"""
        start_time = datetime.now()

        try:
            task_type = task.parameters.get("task_type", "full_prep")

            if task_type == "full_prep":
                result = await self._full_meeting_preparation(task.parameters)
            elif task_type == "attendee_research":
                result = await self._research_attendees(task.parameters)
            elif task_type == "agenda_generation":
                result = await self._create_agenda(task.parameters)
            elif task_type == "briefing_document":
                result = await self._create_briefing(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="success",
                result=result,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    "task_type": task_type,
                    "parameters": task.parameters
                }
            )

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="error",
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    async def _full_meeting_preparation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete meeting preparation"""
        meeting_info = MeetingInfo(**parameters.get("meeting_info", {}))

        self.logger.info(f"Preparing for meeting: {meeting_info.title}")

        # Step 1: Research attendees
        attendee_research = await self._research_attendees({
            "attendees": meeting_info.attendees
        })

        # Step 2: Generate agenda
        agenda = await self._create_agenda({
            "meeting_info": meeting_info.dict(),
            "attendee_research": attendee_research
        })

        # Step 3: Generate talking points
        talking_points = await self._generate_talking_points_for_meeting(
            meeting_info,
            attendee_research
        )

        # Step 4: Create briefing document
        briefing = await self._create_briefing({
            "meeting_info": meeting_info.dict(),
            "attendee_research": attendee_research,
            "agenda": agenda,
            "talking_points": talking_points
        })

        # Step 5: Identify potential outcomes
        outcomes = await self._identify_potential_outcomes(
            meeting_info,
            agenda
        )

        return {
            "meeting": meeting_info.dict(),
            "attendee_research": attendee_research,
            "agenda": agenda,
            "talking_points": talking_points,
            "briefing_document": briefing,
            "potential_outcomes": outcomes,
            "preparation_complete": True,
            "prepared_at": datetime.now().isoformat()
        }

    async def _research_attendees(self, parameters: Dict[str, Any]) -> Dict[str, AttendeeResearch]:
        """Research meeting attendees"""
        attendees = parameters.get("attendees", [])
        research_results = {}

        for attendee in attendees:
            # Check cache first
            if attendee in self.research_cache:
                research_results[attendee] = self.research_cache[attendee]
                continue

            # Perform research
            try:
                # Web search for the person
                search_prompt = f"{attendee} professional background recent news"
                search_result = await self._async_web_search(search_prompt)

                # Analyze search results
                research = AttendeeResearch(
                    name=attendee,
                    background=self._extract_background(search_result),
                    recent_activity=self._extract_recent_activity(search_result),
                    talking_points=self._generate_attendee_talking_points(search_result)
                )

                # Cache the result
                self.research_cache[attendee] = research
                research_results[attendee] = research

            except Exception as e:
                self.logger.warning(f"Failed to research {attendee}: {e}")
                research_results[attendee] = AttendeeResearch(
                    name=attendee,
                    background="Research unavailable",
                    talking_points=["Focus on general professional topics"]
                )

        return research_results

    async def _create_agenda(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a meeting agenda"""
        meeting_info = parameters.get("meeting_info", {})
        attendee_research = parameters.get("attendee_research", {})

        # Select appropriate template
        template = self._select_agenda_template(meeting_info)

        # Generate agenda items
        agenda_items = []

        # Opening
        agenda_items.append({
            "time": "0-5 min",
            "item": "Introduction and objectives",
            "owner": "Host",
            "notes": "Set context and expectations"
        })

        # Main topics based on meeting type
        if "project" in meeting_info.get("topic", "").lower():
            agenda_items.extend(self._generate_project_agenda_items())
        elif "review" in meeting_info.get("topic", "").lower():
            agenda_items.extend(self._generate_review_agenda_items())
        else:
            agenda_items.extend(self._generate_general_agenda_items(meeting_info))

        # Closing
        agenda_items.append({
            "time": f"{meeting_info.get('duration', 60)-10}-{meeting_info.get('duration', 60)} min",
            "item": "Next steps and action items",
            "owner": "All",
            "notes": "Confirm deliverables and timeline"
        })

        return {
            "title": meeting_info.get("title", "Meeting Agenda"),
            "date": meeting_info.get("date"),
            "duration": meeting_info.get("duration", 60),
            "attendees": list(attendee_research.keys()),
            "objectives": self._generate_objectives(meeting_info),
            "agenda_items": agenda_items,
            "pre_meeting_prep": self._generate_prep_requirements(meeting_info)
        }

    async def _create_briefing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive briefing document"""
        meeting_info = parameters.get("meeting_info", {})
        attendee_research = parameters.get("attendee_research", {})
        agenda = parameters.get("agenda", {})
        talking_points = parameters.get("talking_points", [])

        briefing = {
            "executive_summary": self._generate_executive_summary(meeting_info, agenda),
            "meeting_context": {
                "purpose": meeting_info.get("topic", "General discussion"),
                "expected_outcomes": agenda.get("objectives", []),
                "duration": meeting_info.get("duration", 60),
                "format": "In-person" if not meeting_info.get("virtual") else "Virtual"
            },
            "attendee_profiles": self._format_attendee_profiles(attendee_research),
            "key_discussion_points": talking_points,
            "strategic_recommendations": self._generate_recommendations(
                meeting_info,
                attendee_research
            ),
            "risk_factors": self._identify_risks(meeting_info),
            "success_metrics": self._define_success_metrics(meeting_info),
            "follow_up_actions": self._suggest_follow_ups(meeting_info)
        }

        return briefing

    async def _generate_talking_points_for_meeting(
        self,
        meeting_info: MeetingInfo,
        attendee_research: Dict[str, AttendeeResearch]
    ) -> List[str]:
        """Generate key talking points for the meeting"""
        talking_points = []

        # Opening talking points
        talking_points.extend([
            f"Thank everyone for making time for this {meeting_info.topic or 'discussion'}",
            "Brief introduction of the meeting objectives and expected outcomes"
        ])

        # Personalized points based on attendee research
        for attendee_name, research in attendee_research.items():
            if research.talking_points:
                talking_points.append(
                    f"With {attendee_name}: {research.talking_points[0]}"
                )

        # Topic-specific talking points
        if meeting_info.topic:
            talking_points.extend(self._generate_topic_talking_points(meeting_info.topic))

        # Closing talking points
        talking_points.extend([
            "Summarize key decisions and action items",
            "Confirm next steps and timeline",
            "Schedule follow-up if needed"
        ])

        return talking_points

    async def _identify_potential_outcomes(
        self,
        meeting_info: MeetingInfo,
        agenda: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify potential meeting outcomes"""
        outcomes = []

        # Best case scenario
        outcomes.append({
            "scenario": "Best Case",
            "description": "All objectives are met with full alignment",
            "probability": "30%",
            "indicators": [
                "Active engagement from all participants",
                "Clear agreement on next steps",
                "Concrete timeline established"
            ]
        })

        # Likely scenario
        outcomes.append({
            "scenario": "Most Likely",
            "description": "Partial progress with some items requiring follow-up",
            "probability": "50%",
            "indicators": [
                "Good discussion on key topics",
                "Some decisions made",
                "Follow-up needed on complex items"
            ]
        })

        # Challenging scenario
        outcomes.append({
            "scenario": "Challenging",
            "description": "Limited progress due to misalignment or complexity",
            "probability": "20%",
            "indicators": [
                "Disagreement on approach",
                "Need for additional information",
                "Multiple follow-up meetings required"
            ],
            "mitigation": [
                "Prepare alternative proposals",
                "Have data ready to support positions",
                "Be ready to schedule immediate follow-up"
            ]
        })

        return outcomes

    # Helper methods
    async def _async_web_search(self, query: str) -> str:
        """Perform asynchronous web search"""
        # This would use actual web search API
        await asyncio.sleep(0.5)  # Simulate API call
        return f"Search results for: {query}"

    def _linkedin_research(self, attendee: AttendeeResearch) -> Dict[str, Any]:
        """Simulate LinkedIn research"""
        return {
            "name": attendee.name,
            "title": "Professional",
            "company": "TechCorp",
            "connections": ["mutual connections"],
            "recent_posts": ["Recent professional updates"]
        }

    def _generate_agenda(self, context: str) -> str:
        """Generate meeting agenda"""
        return f"Generated agenda based on: {context}"

    def _generate_talking_points(self, context: str) -> str:
        """Generate talking points"""
        return f"Key talking points for: {context}"

    def _load_agenda_templates(self) -> Dict[str, Any]:
        """Load agenda templates"""
        return {
            "project_kickoff": {"sections": ["Introduction", "Goals", "Timeline", "Resources"]},
            "status_review": {"sections": ["Progress", "Blockers", "Next Steps"]},
            "general": {"sections": ["Objectives", "Discussion", "Action Items"]}
        }

    def _load_briefing_template(self) -> Dict[str, Any]:
        """Load briefing document template"""
        return {
            "sections": ["Executive Summary", "Context", "Attendees", "Talking Points"]
        }

    def _extract_background(self, search_result: str) -> str:
        """Extract background information from search results"""
        return "Professional background based on available information"

    def _extract_recent_activity(self, search_result: str) -> str:
        """Extract recent activity from search results"""
        return "Recent professional activity and updates"

    def _generate_attendee_talking_points(self, search_result: str) -> List[str]:
        """Generate talking points based on attendee research"""
        return [
            "Discuss recent industry trends",
            "Explore collaboration opportunities",
            "Share relevant experiences"
        ]

    def _select_agenda_template(self, meeting_info: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate agenda template"""
        topic = meeting_info.get("topic", "").lower()
        if "project" in topic:
            return self.agenda_templates["project_kickoff"]
        elif "review" in topic or "status" in topic:
            return self.agenda_templates["status_review"]
        else:
            return self.agenda_templates["general"]

    def _generate_project_agenda_items(self) -> List[Dict[str, Any]]:
        """Generate agenda items for project meetings"""
        return [
            {"time": "5-15 min", "item": "Project scope and objectives", "owner": "Project Lead"},
            {"time": "15-30 min", "item": "Timeline and milestones", "owner": "Project Manager"},
            {"time": "30-45 min", "item": "Resource allocation", "owner": "Team Lead"},
            {"time": "45-50 min", "item": "Risk assessment", "owner": "All"}
        ]

    def _generate_review_agenda_items(self) -> List[Dict[str, Any]]:
        """Generate agenda items for review meetings"""
        return [
            {"time": "5-20 min", "item": "Progress update", "owner": "Team Members"},
            {"time": "20-35 min", "item": "Challenges and blockers", "owner": "All"},
            {"time": "35-50 min", "item": "Solutions and next steps", "owner": "Team Lead"}
        ]

    def _generate_general_agenda_items(self, meeting_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general agenda items"""
        return [
            {"time": "5-25 min", "item": "Main discussion topic", "owner": "Facilitator"},
            {"time": "25-45 min", "item": "Open discussion", "owner": "All"},
            {"time": "45-50 min", "item": "Decision points", "owner": "Decision Maker"}
        ]

    def _generate_objectives(self, meeting_info: Dict[str, Any]) -> List[str]:
        """Generate meeting objectives"""
        return [
            f"Align on {meeting_info.get('topic', 'key topics')}",
            "Identify action items and owners",
            "Establish timeline for next steps"
        ]

    def _generate_prep_requirements(self, meeting_info: Dict[str, Any]) -> List[str]:
        """Generate pre-meeting preparation requirements"""
        return [
            "Review relevant documents",
            "Prepare questions and discussion points",
            "Gather necessary data or metrics"
        ]

    def _generate_executive_summary(self, meeting_info: Dict[str, Any], agenda: Dict[str, Any]) -> str:
        """Generate executive summary for briefing"""
        return (
            f"Meeting scheduled for {meeting_info.get('date')} to discuss {meeting_info.get('topic', 'key topics')}. "
            f"Key objectives include {', '.join(agenda.get('objectives', [])[:2])}. "
            "Preparation materials and talking points provided below."
        )

    def _format_attendee_profiles(self, attendee_research: Dict[str, AttendeeResearch]) -> List[Dict[str, Any]]:
        """Format attendee profiles for briefing"""
        profiles = []
        for name, research in attendee_research.items():
            profiles.append({
                "name": name,
                "background": research.background,
                "recent_activity": research.recent_activity,
                "engagement_strategy": research.talking_points[:2] if research.talking_points else []
            })
        return profiles

    def _generate_recommendations(
        self,
        meeting_info: Dict[str, Any],
        attendee_research: Dict[str, AttendeeResearch]
    ) -> List[str]:
        """Generate strategic recommendations"""
        return [
            "Start with a clear statement of objectives",
            "Engage each participant with personalized questions",
            "Keep discussion focused on actionable outcomes",
            "Document decisions and next steps clearly"
        ]

    def _identify_risks(self, meeting_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential meeting risks"""
        return [
            {"risk": "Time overrun", "mitigation": "Strict agenda adherence"},
            {"risk": "Lack of preparation", "mitigation": "Send pre-read materials"},
            {"risk": "Technical issues", "mitigation": "Test technology beforehand"}
        ]

    def _define_success_metrics(self, meeting_info: Dict[str, Any]) -> List[str]:
        """Define success metrics for the meeting"""
        return [
            "All agenda items addressed",
            "Clear action items with owners assigned",
            "Timeline for follow-up established",
            "Participant engagement throughout"
        ]

    def _suggest_follow_ups(self, meeting_info: Dict[str, Any]) -> List[str]:
        """Suggest follow-up actions"""
        return [
            "Send meeting summary within 24 hours",
            "Schedule follow-up meetings if needed",
            "Track action item completion",
            "Gather feedback on meeting effectiveness"
        ]

    def _generate_topic_talking_points(self, topic: str) -> List[str]:
        """Generate topic-specific talking points"""
        return [
            f"Current state of {topic}",
            f"Key challenges in {topic}",
            f"Proposed solutions for {topic}",
            f"Success metrics for {topic}"
        ]