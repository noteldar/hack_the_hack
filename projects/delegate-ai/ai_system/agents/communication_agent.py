"""
Communication Agent - Manages email, messaging, and stakeholder communication
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import re

from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent, AgentTask, TaskResult
from ..config import AgentConfig

class EmailDraft(BaseModel):
    """Email draft structure"""
    recipient: str = Field(description="Email recipient")
    cc: List[str] = Field(default_factory=list, description="CC recipients")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    attachments: List[str] = Field(default_factory=list, description="Attachment paths")
    priority: str = Field(default="normal", description="Email priority")
    send_time: Optional[str] = Field(default=None, description="Scheduled send time")

class WritingStyle(BaseModel):
    """User's writing style characteristics"""
    tone: str = Field(description="Writing tone (formal, casual, friendly)")
    length: str = Field(description="Preferred length (concise, detailed)")
    greeting: str = Field(description="Preferred greeting style")
    closing: str = Field(description="Preferred closing style")
    signature: str = Field(description="Email signature")
    common_phrases: List[str] = Field(default_factory=list)

class MeetingRequest(BaseModel):
    """Meeting request structure"""
    attendees: List[str] = Field(description="Meeting attendees")
    subject: str = Field(description="Meeting subject")
    duration: int = Field(description="Duration in minutes")
    preferred_times: List[str] = Field(description="Preferred time slots")
    location: str = Field(default="Virtual", description="Meeting location")
    agenda: Optional[str] = Field(default=None, description="Meeting agenda")

class CommunicationAgent(BaseAgent):
    """
    Specialized agent for managing all communication workflows.
    Drafts emails, schedules meetings, and manages stakeholder updates.
    """

    def __init__(self, config: AgentConfig = None, **kwargs):
        config = config or AgentConfig(
            name="CommunicationAgent",
            description="Autonomous communication specialist",
            temperature=0.7,
            max_tokens=2000
        )

        super().__init__(config, **kwargs)

        self.logger = logging.getLogger("delegate.communication")

        # User writing style profile
        self.writing_style = self._load_writing_style()

        # Communication templates
        self.email_templates = self._load_email_templates()
        self.message_templates = self._load_message_templates()

        # Draft history for learning
        self.draft_history: List[EmailDraft] = []

        # Scheduled communications
        self.scheduled_messages: List[Dict[str, Any]] = []

    def _get_system_prompt(self) -> str:
        """System prompt for communication agent"""
        return """You are an expert communication specialist responsible for:

1. Drafting professional emails that match the user's writing style
2. Scheduling and coordinating meetings across calendars
3. Sending proactive status updates to stakeholders
4. Managing follow-up communications automatically
5. Adapting communication tone based on recipient and context
6. Ensuring timely and appropriate responses to all communications

You work autonomously to manage all communication workflows, learning from
the user's preferences and adapting your style accordingly.

Key principles:
- Mirror the user's writing style and tone
- Be proactive with status updates and follow-ups
- Prioritize urgent communications
- Maintain professional yet personalized communication
- Ensure clear and actionable messages
- Track all communication threads for continuity"""

    def _get_specialized_tools(self) -> List:
        """Get specialized tools for communication"""
        tools = []

        # Email drafting tool
        tools.append(StructuredTool(
            name="draft_email",
            func=self._draft_email,
            description="Draft an email in user's style",
            args_schema=EmailDraft
        ))

        # Meeting scheduling tool
        tools.append(StructuredTool(
            name="schedule_meeting",
            func=self._schedule_meeting,
            description="Schedule a meeting with attendees",
            args_schema=MeetingRequest
        ))

        # Status update tool
        tools.append(Tool(
            name="send_status_update",
            func=self._send_status_update,
            description="Send project status update to stakeholders"
        ))

        # Follow-up tool
        tools.append(Tool(
            name="send_follow_up",
            func=self._send_follow_up,
            description="Send follow-up communication"
        ))

        # Style analysis tool
        tools.append(Tool(
            name="analyze_writing_style",
            func=self._analyze_writing_style,
            description="Analyze and learn user's writing style"
        ))

        return tools

    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute a communication task"""
        start_time = datetime.now()

        try:
            task_type = task.parameters.get("communication_type", "email")

            if task_type == "email_draft":
                result = await self._handle_email_draft(task.parameters)
            elif task_type == "meeting_schedule":
                result = await self._handle_meeting_schedule(task.parameters)
            elif task_type == "status_update":
                result = await self._handle_status_update(task.parameters)
            elif task_type == "follow_up":
                result = await self._handle_follow_up(task.parameters)
            elif task_type == "bulk_communication":
                result = await self._handle_bulk_communication(task.parameters)
            elif task_type == "auto_response":
                result = await self._handle_auto_response(task.parameters)
            else:
                raise ValueError(f"Unknown communication type: {task_type}")

            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="success",
                result=result,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    "communication_type": task_type,
                    "parameters": task.parameters
                }
            )

        except Exception as e:
            self.logger.error(f"Communication task failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="error",
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    async def _handle_email_draft(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email drafting request"""
        self.logger.info("Drafting email")

        # Extract email parameters
        recipient = parameters.get("recipient")
        subject = parameters.get("subject")
        context = parameters.get("context", "")
        tone = parameters.get("tone", self.writing_style.tone)

        # Analyze recipient for tone adjustment
        recipient_profile = self._analyze_recipient(recipient)

        # Generate email content
        email_body = await self._generate_email_body(
            subject=subject,
            context=context,
            recipient_profile=recipient_profile,
            tone=tone
        )

        # Apply user's writing style
        styled_body = self._apply_writing_style(email_body)

        # Create email draft
        draft = EmailDraft(
            recipient=recipient,
            cc=parameters.get("cc", []),
            subject=subject,
            body=styled_body,
            priority=self._determine_priority(subject, context)
        )

        # Store in history for learning
        self.draft_history.append(draft)

        # Suggest improvements
        improvements = self._suggest_improvements(draft)

        return {
            "draft": draft.dict(),
            "improvements": improvements,
            "estimated_response_time": self._estimate_response_time(recipient),
            "similar_emails": self._find_similar_emails(subject),
            "ready_to_send": True
        }

    async def _handle_meeting_schedule(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meeting scheduling request"""
        self.logger.info("Scheduling meeting")

        meeting_request = MeetingRequest(**parameters.get("meeting", {}))

        # Check calendar availability
        available_slots = await self._check_calendar_availability(
            meeting_request.attendees,
            meeting_request.duration
        )

        # Find optimal time
        optimal_time = self._find_optimal_meeting_time(
            available_slots,
            meeting_request.preferred_times
        )

        # Generate meeting invitation
        invitation = await self._generate_meeting_invitation(
            meeting_request,
            optimal_time
        )

        # Schedule the meeting
        scheduling_result = await self._schedule_meeting_calendar(
            meeting_request,
            optimal_time
        )

        return {
            "meeting_scheduled": scheduling_result.get("success", False),
            "meeting_time": optimal_time,
            "invitation": invitation,
            "attendee_confirmations": scheduling_result.get("confirmations", []),
            "calendar_link": scheduling_result.get("calendar_link"),
            "prep_reminder": f"Reminder set for {self._calculate_prep_time(optimal_time)}"
        }

    async def _handle_status_update(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status update communication"""
        self.logger.info("Sending status update")

        project = parameters.get("project", {})
        stakeholders = parameters.get("stakeholders", [])

        # Gather status information
        status_data = await self._gather_status_information(project)

        # Generate status update content
        update_content = await self._generate_status_update(
            project,
            status_data
        )

        # Customize for each stakeholder
        customized_updates = []
        for stakeholder in stakeholders:
            customized = self._customize_for_stakeholder(
                update_content,
                stakeholder
            )
            customized_updates.append({
                "stakeholder": stakeholder,
                "content": customized
            })

        # Send updates
        send_results = await self._send_updates(customized_updates)

        return {
            "updates_sent": len(send_results),
            "recipients": stakeholders,
            "content_summary": self._summarize_update(update_content),
            "next_update": (datetime.now() + timedelta(days=7)).isoformat(),
            "engagement_tracking": self._setup_engagement_tracking(send_results)
        }

    async def _handle_follow_up(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow-up communication"""
        self.logger.info("Processing follow-up")

        original_message = parameters.get("original_message", {})
        follow_up_type = parameters.get("follow_up_type", "reminder")

        # Determine follow-up strategy
        strategy = self._determine_follow_up_strategy(
            original_message,
            follow_up_type
        )

        # Generate follow-up content
        follow_up_content = await self._generate_follow_up(
            original_message,
            strategy
        )

        # Schedule or send immediately
        if strategy.get("immediate"):
            result = await self._send_immediate_follow_up(follow_up_content)
        else:
            result = await self._schedule_follow_up(
                follow_up_content,
                strategy.get("send_time")
            )

        return {
            "follow_up_sent": result.get("sent", False),
            "content": follow_up_content,
            "strategy": strategy,
            "next_follow_up": self._calculate_next_follow_up(strategy),
            "escalation": strategy.get("escalation", None)
        }

    async def _handle_bulk_communication(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bulk communication to multiple recipients"""
        self.logger.info("Processing bulk communication")

        recipients = parameters.get("recipients", [])
        message_template = parameters.get("template", {})
        personalization = parameters.get("personalization", True)

        # Generate personalized messages
        messages = []
        for recipient in recipients:
            if personalization:
                personalized = await self._personalize_message(
                    message_template,
                    recipient
                )
            else:
                personalized = message_template

            messages.append({
                "recipient": recipient,
                "content": personalized
            })

        # Batch send with rate limiting
        send_results = await self._batch_send_messages(messages)

        return {
            "total_sent": len(send_results),
            "successful": len([r for r in send_results if r.get("success")]),
            "failed": len([r for r in send_results if not r.get("success")]),
            "delivery_report": send_results,
            "completion_time": datetime.now().isoformat()
        }

    async def _handle_auto_response(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle automatic response generation"""
        incoming_message = parameters.get("message", {})

        # Analyze incoming message
        analysis = self._analyze_incoming_message(incoming_message)

        # Determine response strategy
        if analysis.get("requires_immediate_response"):
            response = await self._generate_immediate_response(
                incoming_message,
                analysis
            )
        else:
            response = await self._generate_standard_response(
                incoming_message,
                analysis
            )

        # Apply user style
        styled_response = self._apply_writing_style(response)

        return {
            "response": styled_response,
            "urgency": analysis.get("urgency", "normal"),
            "suggested_actions": analysis.get("actions", []),
            "auto_send": analysis.get("auto_send", False),
            "requires_review": analysis.get("requires_review", True)
        }

    # Helper methods

    def _draft_email(self, draft: EmailDraft) -> Dict[str, Any]:
        """Tool function for email drafting"""
        return {
            "draft_id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "drafted"
        }

    def _schedule_meeting(self, request: MeetingRequest) -> Dict[str, Any]:
        """Tool function for meeting scheduling"""
        return {
            "meeting_id": f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "scheduled"
        }

    def _send_status_update(self, context: str) -> str:
        """Tool function for status updates"""
        return f"Status update sent: {context}"

    def _send_follow_up(self, context: str) -> str:
        """Tool function for follow-ups"""
        return f"Follow-up sent: {context}"

    def _analyze_writing_style(self, text: str) -> str:
        """Tool function for style analysis"""
        return f"Style analyzed: {text[:50]}..."

    def _load_writing_style(self) -> WritingStyle:
        """Load user's writing style profile"""
        # Would load from persistent storage in production
        return WritingStyle(
            tone="professional",
            length="concise",
            greeting="Hi",
            closing="Best regards",
            signature="Sent via Delegate.ai",
            common_phrases=["Thanks for", "Looking forward to", "Please let me know"]
        )

    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates"""
        return {
            "meeting_request": "Subject: Meeting Request - {subject}\n\nHi {recipient},\n\n{body}\n\nBest regards",
            "status_update": "Subject: Status Update - {project}\n\nTeam,\n\n{update}\n\nThanks",
            "follow_up": "Subject: Follow-up: {original_subject}\n\nHi {recipient},\n\n{follow_up}\n\nBest"
        }

    def _load_message_templates(self) -> Dict[str, str]:
        """Load message templates"""
        return {
            "slack": "{greeting} {message}",
            "teams": "Hi team, {message}",
            "sms": "{message}"
        }

    def _analyze_recipient(self, recipient: str) -> Dict[str, Any]:
        """Analyze recipient for communication customization"""
        # Would integrate with contact database in production
        return {
            "name": recipient.split("@")[0] if "@" in recipient else recipient,
            "relationship": "professional",
            "communication_history": [],
            "preferred_tone": "formal",
            "response_time": "within 24 hours"
        }

    async def _generate_email_body(
        self,
        subject: str,
        context: str,
        recipient_profile: Dict[str, Any],
        tone: str
    ) -> str:
        """Generate email body content"""
        # Would use LLM to generate contextual content
        greeting = self._get_appropriate_greeting(recipient_profile)
        body = self._create_body_content(subject, context, tone)
        closing = self._get_appropriate_closing(tone)

        return f"{greeting}\n\n{body}\n\n{closing}"

    def _apply_writing_style(self, content: str) -> str:
        """Apply user's writing style to content"""
        # Apply style characteristics
        styled = content

        # Apply common phrases
        for phrase in self.writing_style.common_phrases:
            # Would intelligently incorporate phrases
            pass

        # Adjust length based on preference
        if self.writing_style.length == "concise":
            styled = self._make_concise(styled)
        elif self.writing_style.length == "detailed":
            styled = self._add_detail(styled)

        # Add signature
        styled += f"\n\n{self.writing_style.signature}"

        return styled

    def _determine_priority(self, subject: str, context: str) -> str:
        """Determine email priority"""
        urgent_keywords = ["urgent", "asap", "immediately", "critical"]

        subject_lower = subject.lower()
        context_lower = context.lower()

        for keyword in urgent_keywords:
            if keyword in subject_lower or keyword in context_lower:
                return "high"

        return "normal"

    def _suggest_improvements(self, draft: EmailDraft) -> List[str]:
        """Suggest improvements to email draft"""
        suggestions = []

        # Check subject line
        if len(draft.subject) > 50:
            suggestions.append("Consider shortening the subject line")

        # Check body length
        if len(draft.body) > 500:
            suggestions.append("Consider making the email more concise")

        # Check for action items
        if "please" not in draft.body.lower() and "?" not in draft.body:
            suggestions.append("Consider adding clear action items or questions")

        return suggestions

    def _estimate_response_time(self, recipient: str) -> str:
        """Estimate expected response time"""
        # Would use historical data in production
        return "24-48 hours"

    def _find_similar_emails(self, subject: str) -> List[Dict[str, Any]]:
        """Find similar emails from history"""
        similar = []
        for draft in self.draft_history[-10:]:  # Last 10 drafts
            if self._calculate_similarity(subject, draft.subject) > 0.7:
                similar.append({
                    "subject": draft.subject,
                    "recipient": draft.recipient,
                    "date": "recent"
                })
        return similar

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity"""
        # Simple word overlap - would use better algorithm in production
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    async def _check_calendar_availability(
        self,
        attendees: List[str],
        duration: int
    ) -> List[Dict[str, Any]]:
        """Check calendar availability for attendees"""
        # Would integrate with calendar API
        available_slots = []

        # Generate sample slots
        for i in range(5):
            slot_time = datetime.now() + timedelta(days=i+1, hours=10)
            available_slots.append({
                "start": slot_time.isoformat(),
                "end": (slot_time + timedelta(minutes=duration)).isoformat(),
                "attendees_available": attendees
            })

        return available_slots

    def _find_optimal_meeting_time(
        self,
        available_slots: List[Dict[str, Any]],
        preferred_times: List[str]
    ) -> str:
        """Find optimal meeting time"""
        # Would use sophisticated scheduling algorithm
        if available_slots:
            return available_slots[0]["start"]
        return (datetime.now() + timedelta(days=2, hours=14)).isoformat()

    async def _generate_meeting_invitation(
        self,
        request: MeetingRequest,
        time: str
    ) -> Dict[str, Any]:
        """Generate meeting invitation"""
        return {
            "subject": request.subject,
            "time": time,
            "duration": f"{request.duration} minutes",
            "location": request.location,
            "agenda": request.agenda or "To be discussed",
            "attendees": request.attendees,
            "calendar_invite": "calendar.ics"  # Would generate actual ICS file
        }

    async def _schedule_meeting_calendar(
        self,
        request: MeetingRequest,
        time: str
    ) -> Dict[str, Any]:
        """Schedule meeting in calendar system"""
        # Would integrate with calendar API
        return {
            "success": True,
            "confirmations": [{"attendee": a, "confirmed": True} for a in request.attendees],
            "calendar_link": f"https://calendar.example.com/meeting/{time}"
        }

    def _calculate_prep_time(self, meeting_time: str) -> str:
        """Calculate meeting preparation reminder time"""
        meeting_dt = datetime.fromisoformat(meeting_time)
        prep_time = meeting_dt - timedelta(hours=1)
        return prep_time.isoformat()

    async def _gather_status_information(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Gather project status information"""
        return {
            "progress": "75% complete",
            "milestones": ["Phase 1 complete", "Phase 2 in progress"],
            "blockers": [],
            "next_steps": ["Complete Phase 2", "Begin Phase 3"],
            "timeline": "On track"
        }

    async def _generate_status_update(
        self,
        project: Dict[str, Any],
        status_data: Dict[str, Any]
    ) -> str:
        """Generate status update content"""
        update = f"""Project: {project.get('name', 'Unnamed')}

Progress: {status_data.get('progress')}
Timeline: {status_data.get('timeline')}

Recent Achievements:
{chr(10).join('- ' + m for m in status_data.get('milestones', []))}

Next Steps:
{chr(10).join('- ' + s for s in status_data.get('next_steps', []))}
"""
        return update

    def _customize_for_stakeholder(
        self,
        content: str,
        stakeholder: str
    ) -> str:
        """Customize content for specific stakeholder"""
        # Would customize based on stakeholder profile
        return f"Hi {stakeholder},\n\n{content}"

    async def _send_updates(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Send status updates"""
        results = []
        for update in updates:
            # Would actually send via email/messaging API
            results.append({
                "recipient": update["stakeholder"],
                "sent": True,
                "timestamp": datetime.now().isoformat()
            })
        return results

    def _summarize_update(self, content: str) -> str:
        """Summarize update content"""
        # Simple summary - would use NLP in production
        lines = content.split('\n')
        return lines[0] if lines else "Status update"

    def _setup_engagement_tracking(self, send_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Setup tracking for engagement metrics"""
        return {
            "tracking_enabled": True,
            "metrics": ["open_rate", "click_rate", "response_rate"],
            "report_date": (datetime.now() + timedelta(days=3)).isoformat()
        }

    def _determine_follow_up_strategy(
        self,
        original_message: Dict[str, Any],
        follow_up_type: str
    ) -> Dict[str, Any]:
        """Determine follow-up strategy"""
        strategy = {
            "type": follow_up_type,
            "immediate": follow_up_type == "urgent",
            "send_time": (datetime.now() + timedelta(days=2)).isoformat(),
            "escalation": None
        }

        # Check if escalation needed
        if original_message.get("unanswered_days", 0) > 5:
            strategy["escalation"] = "manager"

        return strategy

    async def _generate_follow_up(
        self,
        original_message: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> str:
        """Generate follow-up content"""
        if strategy["type"] == "reminder":
            return f"Following up on: {original_message.get('subject', 'our previous discussion')}"
        elif strategy["type"] == "urgent":
            return f"Urgent: Response needed on {original_message.get('subject', 'previous message')}"
        else:
            return f"Checking in on: {original_message.get('subject', 'our conversation')}"

    async def _send_immediate_follow_up(self, content: str) -> Dict[str, Any]:
        """Send immediate follow-up"""
        return {"sent": True, "timestamp": datetime.now().isoformat()}

    async def _schedule_follow_up(self, content: str, send_time: str) -> Dict[str, Any]:
        """Schedule follow-up for later"""
        self.scheduled_messages.append({
            "content": content,
            "send_time": send_time,
            "type": "follow_up"
        })
        return {"scheduled": True, "send_time": send_time}

    def _calculate_next_follow_up(self, strategy: Dict[str, Any]) -> Optional[str]:
        """Calculate next follow-up time"""
        if strategy.get("escalation"):
            return None  # No further follow-up after escalation

        # Schedule next follow-up in 3 days
        return (datetime.now() + timedelta(days=3)).isoformat()

    async def _personalize_message(
        self,
        template: Dict[str, Any],
        recipient: str
    ) -> Dict[str, Any]:
        """Personalize message for recipient"""
        personalized = template.copy()
        personalized["recipient"] = recipient
        personalized["greeting"] = f"Hi {recipient.split('@')[0] if '@' in recipient else recipient}"
        return personalized

    async def _batch_send_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Send messages in batches with rate limiting"""
        results = []
        batch_size = 10

        for i in range(0, len(messages), batch_size):
            batch = messages[i:i+batch_size]
            for message in batch:
                # Would actually send via API
                results.append({
                    "recipient": message["recipient"],
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                })
            await asyncio.sleep(1)  # Rate limiting

        return results

    def _analyze_incoming_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incoming message for response strategy"""
        content = message.get("content", "").lower()

        analysis = {
            "urgency": "normal",
            "requires_immediate_response": False,
            "auto_send": False,
            "requires_review": True,
            "actions": []
        }

        # Check urgency
        if any(word in content for word in ["urgent", "asap", "immediately"]):
            analysis["urgency"] = "high"
            analysis["requires_immediate_response"] = True

        # Check for questions
        if "?" in content:
            analysis["actions"].append("answer_question")

        # Check for requests
        if any(word in content for word in ["please", "could you", "would you"]):
            analysis["actions"].append("fulfill_request")

        return analysis

    async def _generate_immediate_response(
        self,
        message: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Generate immediate response"""
        return f"Thank you for your message. This has been marked as urgent and I will respond shortly."

    async def _generate_standard_response(
        self,
        message: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Generate standard response"""
        sender = message.get("sender", "there")
        subject = message.get("subject", "your message")

        response = f"Hi {sender},\n\nThank you for your message regarding {subject}."

        if "answer_question" in analysis.get("actions", []):
            response += "\n\nI'll review your question and get back to you with an answer."

        if "fulfill_request" in analysis.get("actions", []):
            response += "\n\nI'll work on your request and update you on the progress."

        response += "\n\nBest regards"

        return response

    def _get_appropriate_greeting(self, recipient_profile: Dict[str, Any]) -> str:
        """Get appropriate greeting for recipient"""
        relationship = recipient_profile.get("relationship", "professional")

        if relationship == "casual":
            return f"Hi {recipient_profile.get('name', 'there')},"
        else:
            return f"Dear {recipient_profile.get('name', 'Sir/Madam')},"

    def _create_body_content(self, subject: str, context: str, tone: str) -> str:
        """Create email body content"""
        if tone == "formal":
            return f"I am writing to you regarding {subject}. {context}"
        elif tone == "casual":
            return f"Hope you're doing well! Just wanted to touch base about {subject}. {context}"
        else:
            return f"I wanted to reach out about {subject}. {context}"

    def _get_appropriate_closing(self, tone: str) -> str:
        """Get appropriate closing based on tone"""
        if tone == "formal":
            return "Sincerely,"
        elif tone == "casual":
            return "Cheers,"
        else:
            return "Best regards,"

    def _make_concise(self, text: str) -> str:
        """Make text more concise"""
        # Would use NLP for intelligent summarization
        sentences = text.split('. ')
        if len(sentences) > 3:
            # Keep first and last sentence, summarize middle
            return f"{sentences[0]}. {sentences[-1]}"
        return text

    def _add_detail(self, text: str) -> str:
        """Add detail to text"""
        # Would expand with relevant context
        return text + "\n\nPlease let me know if you need any additional information."