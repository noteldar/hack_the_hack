"""
AI Avatar service for personality-based decision making
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.user import User
from app.models.meeting import Meeting
from app.ai.personality import PersonalityFactory, DecisionEngine, DecisionContext
from app.schemas.ai_avatar import DecisionResponse, AvatarStats


class AIAvatarService:
    """Service for AI avatar personality and decision making"""

    def __init__(self):
        self.decision_engines: Dict[int, DecisionEngine] = {}

    async def get_personality_profile(self, user: User) -> Dict[str, Any]:
        """Get user's AI personality profile"""
        profile = PersonalityFactory.create_profile(
            user.avatar_personality,
            user.ai_decision_autonomy
        )
        return profile.to_dict()

    async def generate_personality_profile(self, personality_type: str, autonomy: float, traits: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new personality profile"""
        profile = PersonalityFactory.create_profile(personality_type, autonomy)

        # Apply custom traits if provided
        for trait_name, value in traits.items():
            if hasattr(profile.traits, trait_name):
                profile.traits[trait_name] = value

        return profile.to_dict()

    def get_decision_engine(self, user: User) -> DecisionEngine:
        """Get or create decision engine for user"""
        if user.id not in self.decision_engines:
            profile = PersonalityFactory.create_profile(
                user.avatar_personality,
                user.ai_decision_autonomy
            )
            self.decision_engines[user.id] = DecisionEngine(profile)

        return self.decision_engines[user.id]

    async def make_decision(self, user: User, scenario: str, context: Dict[str, Any], meeting: Optional[Meeting] = None) -> DecisionResponse:
        """Make an AI decision based on user's personality"""
        engine = self.get_decision_engine(user)

        # Map scenario to decision context
        decision_context = self._map_scenario_to_context(scenario)

        # Enhance context with meeting data if available
        if meeting:
            context.update({
                "meeting_id": meeting.id,
                "importance_score": meeting.ai_importance_score or 0.5,
                "conflict_score": meeting.ai_conflict_score or 0.0,
                "priority": meeting.priority,
                "duration_minutes": meeting.duration_minutes
            })

        # Make decision
        result = engine.make_decision(decision_context, context)

        return DecisionResponse(
            decision_type=result["decision"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            suggested_actions=result.get("suggested_actions", []),
            timestamp=datetime.utcnow()
        )

    async def analyze_meeting(self, meeting_id: int, user_id: int):
        """Analyze a meeting and make AI decision"""
        # This would be implemented with actual meeting analysis logic
        # For now, return a mock analysis
        pass

    async def get_decision_history(self, user_id: int, limit: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get AI decision history for user"""
        engine = self.decision_engines.get(user_id)
        if not engine:
            return []

        history = engine.decision_history[-limit:] if engine.decision_history else []
        return history

    async def get_avatar_stats(self, user_id: int, days: int, db: AsyncSession) -> AvatarStats:
        """Get AI avatar performance statistics"""
        engine = self.decision_engines.get(user_id)

        if not engine:
            return AvatarStats(
                total_decisions=0,
                decisions_accepted=0,
                decisions_rejected=0,
                accuracy_rate=0.0,
                avg_confidence=0.0,
                time_saved_hours=0.0,
                personality_type="professional"
            )

        stats = engine.get_decision_stats()

        return AvatarStats(
            total_decisions=stats.get("total_decisions", 0),
            decisions_accepted=0,  # Would track from user feedback
            decisions_rejected=0,  # Would track from user feedback
            accuracy_rate=0.0,    # Would calculate from feedback
            avg_confidence=stats.get("average_confidence", 0.0),
            time_saved_hours=0.0, # Would calculate from automated decisions
            personality_type=engine.personality.personality_type
        )

    async def train_from_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train AI from user feedback"""
        engine = self.decision_engines.get(user_id)
        if not engine:
            return {"improvements": [], "accuracy_improvement": 0}

        decision_id = feedback_data.get("decision_id")
        if decision_id:
            engine.learn_from_feedback(decision_id, feedback_data)

        return {
            "improvements": ["Decision threshold adjusted", "Pattern recognition updated"],
            "accuracy_improvement": 0.05  # Mock improvement
        }

    async def get_suggestions(self, user: User, context: str, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get AI suggestions for productivity and scheduling"""
        engine = self.get_decision_engine(user)

        # Generate suggestions based on personality and context
        suggestions = []

        if context == "productivity":
            suggestions.extend([
                {
                    "type": "focus_time",
                    "title": "Schedule Focus Block",
                    "description": "Block 2 hours for deep work based on your patterns",
                    "confidence": 0.8,
                    "action": "schedule_focus_time"
                },
                {
                    "type": "meeting_optimization",
                    "title": "Consolidate Meetings",
                    "description": "Group similar meetings to minimize context switching",
                    "confidence": 0.7,
                    "action": "optimize_schedule"
                }
            ])

        elif context == "scheduling":
            suggestions.extend([
                {
                    "type": "conflict_resolution",
                    "title": "Resolve Calendar Conflicts",
                    "description": "3 meetings have scheduling conflicts this week",
                    "confidence": 0.9,
                    "action": "resolve_conflicts"
                }
            ])

        return suggestions

    async def bulk_analyze_meetings(self, user_id: int, days_ahead: int):
        """Bulk analyze upcoming meetings"""
        # This would implement bulk meeting analysis
        # For hackathon purposes, this is a placeholder
        pass

    def _map_scenario_to_context(self, scenario: str) -> DecisionContext:
        """Map scenario string to DecisionContext enum"""
        mapping = {
            "meeting_invitation": DecisionContext.MEETING_INVITATION,
            "scheduling_conflict": DecisionContext.CONFLICT_RESOLUTION,
            "reschedule_request": DecisionContext.CONFLICT_RESOLUTION,
            "focus_time_protection": DecisionContext.FOCUS_TIME_PROTECTION,
            "optimization_decision": DecisionContext.SCHEDULE_OPTIMIZATION
        }

        return mapping.get(scenario, DecisionContext.MEETING_INVITATION)