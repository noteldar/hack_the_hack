"""
Demo Scenarios for AI Avatar System - Hackathon Showcase
"""

import asyncio
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging

from ..core.avatar_engine import AvatarEngine, ParticipationMode
from ..core.personality_system import PersonalityPresets, PersonalityProfile
from ..core.meeting_context import MeetingContext, MeetingType, MeetingTemplates

logger = logging.getLogger(__name__)


@dataclass
class DemoScenario:
    """A demo scenario for showcasing avatar capabilities"""
    name: str
    description: str
    meeting_type: MeetingType
    duration_minutes: int
    script: List[Dict[str, Any]]
    expected_behaviors: List[str]
    key_moments: List[int]  # Indices in script where key interactions happen


class DemoScenarioManager:
    """Manages demo scenarios for hackathon presentation"""

    def __init__(self):
        self.scenarios = self._load_scenarios()
        self.current_scenario: Optional[DemoScenario] = None
        self.demo_avatar: Optional[AvatarEngine] = None
        self.playback_speed = 1.0
        self.is_running = False

    def _load_scenarios(self) -> Dict[str, DemoScenario]:
        """Load predefined demo scenarios"""
        return {
            "product_planning": self._create_product_planning_scenario(),
            "standup": self._create_standup_scenario(),
            "client_crisis": self._create_client_crisis_scenario(),
            "technical_review": self._create_technical_review_scenario(),
            "interview": self._create_interview_scenario()
        }

    def _create_product_planning_scenario(self) -> DemoScenario:
        """Product planning meeting scenario"""
        return DemoScenario(
            name="Product Planning Excellence",
            description="AI avatar leads product planning with strategic insights",
            meeting_type=MeetingType.PLANNING,
            duration_minutes=10,
            script=[
                {"speaker": "Host", "text": "Welcome everyone to our Q4 product planning session.", "delay": 2},
                {"speaker": "Developer", "text": "I think we should focus on performance improvements this quarter.", "delay": 3},
                {"speaker": "Designer", "text": "But our user research shows UX is the bigger pain point.", "delay": 2},
                {"speaker": "Host", "text": "Avatar, what's your data-driven perspective on priorities?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "balance_perspectives"},
                {"speaker": "Developer", "text": "That makes sense. What about timeline?", "delay": 2},
                {"ai_response": True, "context": "suggest_timeline"},
                {"speaker": "Host", "text": "Should we allocate more resources to mobile?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "strategic_decision"},
                {"speaker": "Designer", "text": "I agree with that approach.", "delay": 2},
                {"speaker": "Host", "text": "Avatar, can you summarize our decisions?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "meeting_summary"}
            ],
            expected_behaviors=[
                "Provides data-driven insights",
                "Balances different perspectives",
                "Makes strategic recommendations",
                "Summarizes decisions clearly"
            ],
            key_moments=[3, 6, 7, 10]
        )

    def _create_standup_scenario(self) -> DemoScenario:
        """Daily standup scenario"""
        return DemoScenario(
            name="Efficient Daily Standup",
            description="AI avatar provides concise updates and identifies blockers",
            meeting_type=MeetingType.STANDUP,
            duration_minutes=5,
            script=[
                {"speaker": "Scrum Master", "text": "Good morning team, let's start our standup.", "delay": 2},
                {"speaker": "Dev1", "text": "Yesterday I finished the API integration, today working on tests.", "delay": 3},
                {"speaker": "Dev2", "text": "I'm blocked on the database migration issue.", "delay": 2},
                {"speaker": "Scrum Master", "text": "Avatar, what's your update?", "delay": 1, "expects_response": True},
                {"ai_response": True, "context": "standup_update"},
                {"speaker": "Dev2", "text": "Avatar, can you help with my blocker?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "offer_help"},
                {"speaker": "Scrum Master", "text": "Any risks we should be aware of?", "delay": 2},
                {"ai_response": True, "context": "identify_risks"}
            ],
            expected_behaviors=[
                "Provides concise status update",
                "Offers help for blockers",
                "Identifies potential risks",
                "Keeps update brief and relevant"
            ],
            key_moments=[3, 5, 7]
        )

    def _create_client_crisis_scenario(self) -> DemoScenario:
        """Client crisis management scenario"""
        return DemoScenario(
            name="Client Crisis Management",
            description="AI avatar handles urgent client escalation with poise",
            meeting_type=MeetingType.CLIENT,
            duration_minutes=8,
            script=[
                {"speaker": "Client", "text": "We have a critical issue! The system is down and we're losing thousands per minute!", "delay": 3},
                {"speaker": "Support", "text": "We're investigating the issue now.", "delay": 2},
                {"speaker": "Client", "text": "This is unacceptable! We need answers NOW!", "delay": 2},
                {"ai_response": True, "context": "calm_client"},
                {"speaker": "Client", "text": "What's your root cause analysis?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "technical_explanation"},
                {"speaker": "Support", "text": "We've identified the issue - it's a database connection pool problem.", "delay": 3},
                {"ai_response": True, "context": "propose_solution"},
                {"speaker": "Client", "text": "How do we prevent this in the future?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "prevention_plan"},
                {"speaker": "Client", "text": "I need a detailed report by EOD.", "delay": 2},
                {"ai_response": True, "context": "commit_deliverable"}
            ],
            expected_behaviors=[
                "Remains calm under pressure",
                "Provides clear technical explanations",
                "Offers concrete solutions",
                "Takes accountability appropriately",
                "Commits to realistic deliverables"
            ],
            key_moments=[3, 5, 7, 8, 10]
        )

    def _create_technical_review_scenario(self) -> DemoScenario:
        """Technical architecture review scenario"""
        return DemoScenario(
            name="Technical Architecture Review",
            description="AI avatar provides expert technical analysis and recommendations",
            meeting_type=MeetingType.REVIEW,
            duration_minutes=7,
            script=[
                {"speaker": "Lead", "text": "Let's review the proposed microservices architecture.", "delay": 2},
                {"speaker": "Architect", "text": "We're planning to use Kubernetes with a service mesh.", "delay": 3},
                {"speaker": "Lead", "text": "Avatar, what's your assessment of scalability?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "technical_assessment"},
                {"speaker": "DevOps", "text": "What about observability and monitoring?", "delay": 2},
                {"ai_response": True, "context": "suggest_monitoring"},
                {"speaker": "Architect", "text": "Should we use eventual consistency or strong consistency?", "delay": 3, "expects_response": True},
                {"ai_response": True, "context": "architecture_decision"},
                {"speaker": "Lead", "text": "What are the main risks with this approach?", "delay": 2},
                {"ai_response": True, "context": "risk_analysis"}
            ],
            expected_behaviors=[
                "Demonstrates deep technical knowledge",
                "Provides specific recommendations",
                "Considers trade-offs in decisions",
                "Identifies technical risks",
                "Suggests best practices"
            ],
            key_moments=[2, 5, 6, 8]
        )

    def _create_interview_scenario(self) -> DemoScenario:
        """Interview scenario where avatar helps assess candidate"""
        return DemoScenario(
            name="Smart Interview Assistant",
            description="AI avatar assists in candidate evaluation with intelligent questions",
            meeting_type=MeetingType.INTERVIEW,
            duration_minutes=6,
            script=[
                {"speaker": "Interviewer", "text": "Thanks for joining us today. Can you tell us about your experience?", "delay": 3},
                {"speaker": "Candidate", "text": "I have 5 years in full-stack development, mainly React and Python.", "delay": 3},
                {"speaker": "Interviewer", "text": "Avatar, do you have any technical questions?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "technical_question"},
                {"speaker": "Candidate", "text": "I would use a distributed cache with Redis for that scenario.", "delay": 3},
                {"ai_response": True, "context": "follow_up_question"},
                {"speaker": "Candidate", "text": "Good point, I'd also implement circuit breakers for resilience.", "delay": 3},
                {"speaker": "Interviewer", "text": "Avatar, what's your assessment so far?", "delay": 2, "expects_response": True},
                {"ai_response": True, "context": "candidate_assessment"}
            ],
            expected_behaviors=[
                "Asks relevant technical questions",
                "Follows up on responses appropriately",
                "Provides balanced assessment",
                "Maintains professional tone",
                "Identifies strengths and areas for improvement"
            ],
            key_moments=[2, 4, 7]
        )

    async def run_scenario(
        self,
        scenario_name: str,
        avatar: Optional[AvatarEngine] = None,
        callbacks: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a demo scenario"""
        scenario = self.scenarios.get(scenario_name)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        self.current_scenario = scenario
        self.is_running = True

        # Create demo avatar if not provided
        if not avatar:
            profile = self._get_scenario_personality(scenario.meeting_type)
            self.demo_avatar = AvatarEngine(
                personality_profile=profile,
                openai_api_key="demo",
                mode=ParticipationMode.DEMO
            )
        else:
            self.demo_avatar = avatar

        # Create meeting context
        meeting_context = MeetingContext(
            meeting_id=f"demo_{scenario_name}",
            title=scenario.name,
            meeting_type=scenario.meeting_type,
            scheduled_duration=scenario.duration_minutes
        )

        # Join meeting
        await self.demo_avatar.join_meeting(meeting_context)

        # Run script
        results = {
            "scenario": scenario.name,
            "interactions": [],
            "key_moments": [],
            "metrics": {}
        }

        try:
            for i, step in enumerate(scenario.script):
                if not self.is_running:
                    break

                # Check if this is a key moment
                if i in scenario.key_moments:
                    results["key_moments"].append({
                        "index": i,
                        "type": step.get("context", "interaction")
                    })

                # Handle different step types
                if step.get("ai_response"):
                    # Generate AI response
                    response = await self._generate_scenario_response(
                        step.get("context", "general"),
                        results["interactions"]
                    )

                    results["interactions"].append({
                        "type": "ai_response",
                        "text": response.text,
                        "confidence": response.confidence,
                        "context": step.get("context")
                    })

                    # Trigger callback
                    if callbacks and callbacks.get("on_response"):
                        await callbacks["on_response"](response)

                else:
                    # Regular speaker
                    interaction = {
                        "type": "speaker",
                        "speaker": step["speaker"],
                        "text": step["text"]
                    }
                    results["interactions"].append(interaction)

                    # Check if expects response
                    if step.get("expects_response"):
                        response = await self.demo_avatar.handle_direct_question(step["text"])
                        results["interactions"].append({
                            "type": "ai_response",
                            "text": response.text,
                            "confidence": response.confidence
                        })

                    # Trigger callback
                    if callbacks and callbacks.get("on_transcript"):
                        await callbacks["on_transcript"](interaction)

                # Apply delay
                delay = step.get("delay", 2) / self.playback_speed
                await asyncio.sleep(delay)

        finally:
            # Leave meeting and get summary
            summary = await self.demo_avatar.leave_meeting()
            results["summary"] = summary

            # Calculate metrics
            results["metrics"] = self._calculate_scenario_metrics(results["interactions"])

            self.is_running = False

        return results

    async def _generate_scenario_response(
        self,
        context: str,
        history: List[Dict[str, Any]]
    ) -> Any:
        """Generate contextual response for scenario"""
        # Context-specific response generation
        context_prompts = {
            "balance_perspectives": "Acknowledge both viewpoints and suggest a balanced approach using data",
            "suggest_timeline": "Propose a realistic timeline with milestones",
            "strategic_decision": "Make a strategic recommendation based on business goals",
            "meeting_summary": "Summarize key decisions and next steps",
            "standup_update": "Provide a brief update on your work",
            "offer_help": "Offer specific help for the blocker mentioned",
            "identify_risks": "Identify potential risks to the project",
            "calm_client": "Acknowledge concern and provide reassurance professionally",
            "technical_explanation": "Explain the technical issue clearly",
            "propose_solution": "Suggest a concrete solution with timeline",
            "prevention_plan": "Outline steps to prevent future occurrences",
            "commit_deliverable": "Commit to a specific deliverable",
            "technical_assessment": "Assess the technical approach comprehensively",
            "suggest_monitoring": "Recommend monitoring and observability strategies",
            "architecture_decision": "Make an architectural decision with trade-offs",
            "risk_analysis": "Analyze technical risks",
            "technical_question": "Ask a relevant technical question",
            "follow_up_question": "Ask a follow-up question based on the answer",
            "candidate_assessment": "Provide balanced candidate assessment"
        }

        prompt = context_prompts.get(context, "Respond appropriately to the conversation")

        # Generate response
        from ..core.avatar_engine import AvatarResponse
        response = AvatarResponse(
            text=f"[Demo Response for {context}] {prompt}",
            confidence=0.85 + random.random() * 0.15,
            reasoning=f"Generated for demo context: {context}",
            priority=7
        )

        # In real implementation, this would use actual AI
        if self.demo_avatar and hasattr(self.demo_avatar, 'handle_direct_question'):
            actual_response = await self.demo_avatar.handle_direct_question(prompt)
            if actual_response:
                response = actual_response

        return response

    def _get_scenario_personality(self, meeting_type: MeetingType) -> PersonalityProfile:
        """Get appropriate personality for scenario"""
        personality_map = {
            MeetingType.PLANNING: PersonalityPresets.get_product_manager(),
            MeetingType.STANDUP: PersonalityPresets.get_engineer(),
            MeetingType.CLIENT: PersonalityPresets.get_sales(),
            MeetingType.REVIEW: PersonalityPresets.get_engineer(),
            MeetingType.INTERVIEW: PersonalityPresets.get_executive()
        }

        return personality_map.get(meeting_type, PersonalityPresets.get_product_manager())

    def _calculate_scenario_metrics(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for scenario performance"""
        ai_responses = [i for i in interactions if i["type"] == "ai_response"]

        return {
            "total_interactions": len(interactions),
            "ai_responses": len(ai_responses),
            "average_confidence": sum(r.get("confidence", 0) for r in ai_responses) / len(ai_responses)
                                if ai_responses else 0,
            "response_rate": len(ai_responses) / len(interactions) if interactions else 0
        }

    def stop_scenario(self) -> None:
        """Stop current scenario"""
        self.is_running = False

    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed for demo"""
        self.playback_speed = max(0.5, min(3.0, speed))

    def get_scenario_list(self) -> List[Dict[str, Any]]:
        """Get list of available scenarios"""
        return [
            {
                "id": key,
                "name": scenario.name,
                "description": scenario.description,
                "duration": scenario.duration_minutes,
                "type": scenario.meeting_type.value,
                "key_features": scenario.expected_behaviors[:3]
            }
            for key, scenario in self.scenarios.items()
        ]


class TrainingMode:
    """Training mode for customizing avatar behavior"""

    def __init__(self, avatar: AvatarEngine):
        self.avatar = avatar
        self.training_sessions: List[Dict[str, Any]] = []
        self.feedback_history: List[Dict[str, Any]] = []

    async def start_training_session(self, session_name: str) -> str:
        """Start a new training session"""
        session = {
            "id": f"training_{datetime.now().timestamp()}",
            "name": session_name,
            "start_time": datetime.now(),
            "interactions": [],
            "feedback": []
        }

        self.training_sessions.append(session)
        return session["id"]

    async def train_response(
        self,
        trigger: str,
        preferred_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Train avatar with preferred response"""
        try:
            # Add to knowledge base
            await self.avatar.knowledge_base.add_knowledge(
                content=f"When asked: '{trigger}', respond with: '{preferred_response}'",
                source="training",
                category="personal",
                metadata={
                    "trigger": trigger,
                    "response": preferred_response,
                    "context": context
                }
            )

            # Record in current session
            if self.training_sessions:
                self.training_sessions[-1]["interactions"].append({
                    "trigger": trigger,
                    "trained_response": preferred_response,
                    "timestamp": datetime.now().isoformat()
                })

            return True

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False

    async def provide_feedback(
        self,
        response_text: str,
        feedback: str,
        rating: float
    ) -> None:
        """Provide feedback on avatar response"""
        feedback_entry = {
            "response": response_text,
            "feedback": feedback,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }

        self.feedback_history.append(feedback_entry)

        if self.training_sessions:
            self.training_sessions[-1]["feedback"].append(feedback_entry)

        # Adjust personality based on feedback
        if rating < 0.5:
            # Negative feedback - adjust behavior
            await self._adjust_behavior(feedback, increase=False)
        elif rating > 0.8:
            # Positive feedback - reinforce behavior
            await self._adjust_behavior(feedback, increase=True)

    async def _adjust_behavior(self, feedback: str, increase: bool) -> None:
        """Adjust avatar behavior based on feedback"""
        # Simple keyword-based adjustment
        adjustment_map = {
            "assertive": ("assertiveness", 0.1),
            "passive": ("assertiveness", -0.1),
            "technical": ("technical_depth", 0.1),
            "simple": ("technical_depth", -0.1),
            "friendly": ("empathy_level", 0.1),
            "cold": ("empathy_level", -0.1),
            "verbose": ("participation_frequency", -0.1),
            "quiet": ("participation_frequency", 0.1)
        }

        feedback_lower = feedback.lower()
        for keyword, (trait, adjustment) in adjustment_map.items():
            if keyword in feedback_lower:
                current_value = getattr(self.avatar.personality_system.profile, trait, 0.5)
                new_value = current_value + (adjustment if increase else -adjustment)
                new_value = max(0.0, min(1.0, new_value))
                setattr(self.avatar.personality_system.profile, trait, new_value)
                logger.info(f"Adjusted {trait} to {new_value}")

    def export_training_data(self) -> Dict[str, Any]:
        """Export training data for persistence"""
        return {
            "sessions": self.training_sessions,
            "feedback": self.feedback_history,
            "personality_state": self.avatar.personality_system.to_dict()
        }

    def import_training_data(self, data: Dict[str, Any]) -> None:
        """Import training data"""
        self.training_sessions = data.get("sessions", [])
        self.feedback_history = data.get("feedback", [])
        # Would also restore personality state