"""
AI Avatar Personality Modeling System
"""

import json
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PersonalityTrait(Enum):
    """Core personality traits for AI avatar"""
    ASSERTIVENESS = "assertiveness"
    COLLABORATION = "collaboration"
    EFFICIENCY = "efficiency"
    PROTECTION = "protection"
    ADAPTABILITY = "adaptability"
    COMMUNICATION = "communication"
    DECISION_SPEED = "decision_speed"
    RISK_TOLERANCE = "risk_tolerance"


class DecisionContext(Enum):
    """Different contexts for decision making"""
    MEETING_INVITATION = "meeting_invitation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    SCHEDULE_OPTIMIZATION = "schedule_optimization"
    FOCUS_TIME_PROTECTION = "focus_time_protection"
    DELEGATION = "delegation"
    COMMUNICATION = "communication"


@dataclass
class PersonalityProfile:
    """Comprehensive personality profile for AI avatar"""
    personality_type: str
    traits: Dict[PersonalityTrait, float]  # 0.0 to 1.0 scale
    decision_patterns: Dict[DecisionContext, Dict[str, float]]
    communication_style: Dict[str, Any]
    learning_preferences: Dict[str, float]
    created_at: datetime
    version: str = "1.0"

    def get_trait_score(self, trait: PersonalityTrait) -> float:
        """Get score for a specific trait"""
        return self.traits.get(trait, 0.5)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "personality_type": self.personality_type,
            "traits": {trait.value: score for trait, score in self.traits.items()},
            "decision_patterns": {
                context.value: patterns for context, patterns in self.decision_patterns.items()
            },
            "communication_style": self.communication_style,
            "learning_preferences": self.learning_preferences,
            "created_at": self.created_at.isoformat(),
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityProfile':
        """Create from dictionary"""
        return cls(
            personality_type=data["personality_type"],
            traits={PersonalityTrait(k): v for k, v in data["traits"].items()},
            decision_patterns={
                DecisionContext(k): v for k, v in data["decision_patterns"].items()
            },
            communication_style=data["communication_style"],
            learning_preferences=data["learning_preferences"],
            created_at=datetime.fromisoformat(data["created_at"]),
            version=data.get("version", "1.0")
        )


class PersonalityFactory:
    """Factory for creating personality profiles"""

    PERSONALITY_TEMPLATES = {
        "professional": {
            "traits": {
                PersonalityTrait.ASSERTIVENESS: 0.6,
                PersonalityTrait.COLLABORATION: 0.7,
                PersonalityTrait.EFFICIENCY: 0.8,
                PersonalityTrait.PROTECTION: 0.5,
                PersonalityTrait.ADAPTABILITY: 0.6,
                PersonalityTrait.COMMUNICATION: 0.7,
                PersonalityTrait.DECISION_SPEED: 0.6,
                PersonalityTrait.RISK_TOLERANCE: 0.4
            },
            "communication_style": {
                "formality": 0.8,
                "directness": 0.6,
                "empathy": 0.7,
                "detail_level": 0.7
            }
        },
        "assertive": {
            "traits": {
                PersonalityTrait.ASSERTIVENESS: 0.9,
                PersonalityTrait.COLLABORATION: 0.4,
                PersonalityTrait.EFFICIENCY: 0.9,
                PersonalityTrait.PROTECTION: 0.8,
                PersonalityTrait.ADAPTABILITY: 0.5,
                PersonalityTrait.COMMUNICATION: 0.6,
                PersonalityTrait.DECISION_SPEED: 0.8,
                PersonalityTrait.RISK_TOLERANCE: 0.6
            },
            "communication_style": {
                "formality": 0.6,
                "directness": 0.9,
                "empathy": 0.4,
                "detail_level": 0.5
            }
        },
        "collaborative": {
            "traits": {
                PersonalityTrait.ASSERTIVENESS: 0.3,
                PersonalityTrait.COLLABORATION: 0.9,
                PersonalityTrait.EFFICIENCY: 0.6,
                PersonalityTrait.PROTECTION: 0.4,
                PersonalityTrait.ADAPTABILITY: 0.8,
                PersonalityTrait.COMMUNICATION: 0.9,
                PersonalityTrait.DECISION_SPEED: 0.4,
                PersonalityTrait.RISK_TOLERANCE: 0.7
            },
            "communication_style": {
                "formality": 0.5,
                "directness": 0.4,
                "empathy": 0.9,
                "detail_level": 0.8
            }
        },
        "protective": {
            "traits": {
                PersonalityTrait.ASSERTIVENESS: 0.7,
                PersonalityTrait.COLLABORATION: 0.5,
                PersonalityTrait.EFFICIENCY: 0.7,
                PersonalityTrait.PROTECTION: 0.9,
                PersonalityTrait.ADAPTABILITY: 0.4,
                PersonalityTrait.COMMUNICATION: 0.6,
                PersonalityTrait.DECISION_SPEED: 0.7,
                PersonalityTrait.RISK_TOLERANCE: 0.2
            },
            "communication_style": {
                "formality": 0.7,
                "directness": 0.8,
                "empathy": 0.6,
                "detail_level": 0.9
            }
        },
        "efficient": {
            "traits": {
                PersonalityTrait.ASSERTIVENESS: 0.7,
                PersonalityTrait.COLLABORATION: 0.6,
                PersonalityTrait.EFFICIENCY: 0.95,
                PersonalityTrait.PROTECTION: 0.6,
                PersonalityTrait.ADAPTABILITY: 0.7,
                PersonalityTrait.COMMUNICATION: 0.5,
                PersonalityTrait.DECISION_SPEED: 0.9,
                PersonalityTrait.RISK_TOLERANCE: 0.5
            },
            "communication_style": {
                "formality": 0.6,
                "directness": 0.8,
                "empathy": 0.5,
                "detail_level": 0.4
            }
        }
    }

    @classmethod
    def create_profile(cls, personality_type: str, autonomy: float = 0.5) -> PersonalityProfile:
        """Create a personality profile"""
        template = cls.PERSONALITY_TEMPLATES.get(personality_type, cls.PERSONALITY_TEMPLATES["professional"])

        # Adjust traits based on autonomy level
        adjusted_traits = {}
        for trait, base_score in template["traits"].items():
            if trait in [PersonalityTrait.ASSERTIVENESS, PersonalityTrait.DECISION_SPEED]:
                adjusted_traits[trait] = min(1.0, base_score + (autonomy - 0.5) * 0.4)
            elif trait in [PersonalityTrait.COLLABORATION]:
                adjusted_traits[trait] = max(0.0, base_score - (autonomy - 0.5) * 0.3)
            else:
                adjusted_traits[trait] = base_score

        # Create decision patterns
        decision_patterns = cls._create_decision_patterns(adjusted_traits, autonomy)

        return PersonalityProfile(
            personality_type=personality_type,
            traits=adjusted_traits,
            decision_patterns=decision_patterns,
            communication_style=template["communication_style"],
            learning_preferences=cls._create_learning_preferences(autonomy),
            created_at=datetime.utcnow()
        )

    @classmethod
    def _create_decision_patterns(cls, traits: Dict[PersonalityTrait, float], autonomy: float) -> Dict[DecisionContext, Dict[str, float]]:
        """Create decision patterns based on traits"""
        patterns = {}

        # Meeting invitation patterns
        patterns[DecisionContext.MEETING_INVITATION] = {
            "auto_accept_threshold": 0.3 + traits[PersonalityTrait.COLLABORATION] * 0.4,
            "auto_decline_threshold": 0.7 - traits[PersonalityTrait.ASSERTIVENESS] * 0.3,
            "request_info_probability": 0.2 + traits[PersonalityTrait.COMMUNICATION] * 0.3,
            "suggest_alternative_probability": 0.1 + traits[PersonalityTrait.ADAPTABILITY] * 0.4
        }

        # Conflict resolution patterns
        patterns[DecisionContext.CONFLICT_RESOLUTION] = {
            "reschedule_preference": traits[PersonalityTrait.ADAPTABILITY] * 0.8 + 0.2,
            "priority_override_threshold": 0.8 - traits[PersonalityTrait.COLLABORATION] * 0.3,
            "escalation_threshold": 0.6 + traits[PersonalityTrait.ASSERTIVENESS] * 0.3,
            "compromise_willingness": traits[PersonalityTrait.COLLABORATION] * 0.7 + 0.3
        }

        # Focus time protection patterns
        patterns[DecisionContext.FOCUS_TIME_PROTECTION] = {
            "protection_strength": traits[PersonalityTrait.PROTECTION] * 0.8 + 0.2,
            "interruption_tolerance": 1.0 - traits[PersonalityTrait.EFFICIENCY] * 0.6,
            "block_duration_preference": traits[PersonalityTrait.EFFICIENCY] * 120 + 60,  # minutes
            "flexibility_window": (1.0 - traits[PersonalityTrait.PROTECTION]) * 30 + 15  # minutes
        }

        return patterns

    @classmethod
    def _create_learning_preferences(cls, autonomy: float) -> Dict[str, float]:
        """Create learning preferences"""
        return {
            "feedback_sensitivity": 0.7 + (1.0 - autonomy) * 0.3,
            "adaptation_rate": 0.1 + autonomy * 0.2,
            "pattern_recognition": 0.8,
            "user_override_weight": 1.0 - autonomy * 0.5
        }


class DecisionEngine:
    """AI decision-making engine based on personality"""

    def __init__(self, personality_profile: PersonalityProfile):
        self.personality = personality_profile
        self.decision_history: List[Dict[str, Any]] = []

    def make_decision(self, context: DecisionContext, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on personality and context"""
        patterns = self.personality.decision_patterns.get(context, {})

        if context == DecisionContext.MEETING_INVITATION:
            return self._decide_meeting_invitation(data, patterns)
        elif context == DecisionContext.CONFLICT_RESOLUTION:
            return self._decide_conflict_resolution(data, patterns)
        elif context == DecisionContext.FOCUS_TIME_PROTECTION:
            return self._decide_focus_time_protection(data, patterns)
        else:
            return self._generic_decision(data, patterns)

    def _decide_meeting_invitation(self, data: Dict[str, Any], patterns: Dict[str, float]) -> Dict[str, Any]:
        """Decide on meeting invitation"""
        meeting_importance = data.get("importance_score", 0.5)
        conflict_level = data.get("conflict_score", 0.0)
        organizer_priority = data.get("organizer_priority", 0.5)

        # Calculate decision score
        accept_score = (
            meeting_importance * 0.4 +
            organizer_priority * 0.3 +
            (1.0 - conflict_level) * 0.3
        )

        auto_accept_threshold = patterns.get("auto_accept_threshold", 0.7)
        auto_decline_threshold = patterns.get("auto_decline_threshold", 0.3)

        if accept_score >= auto_accept_threshold:
            decision = "auto_accept"
            confidence = accept_score
            reasoning = "High importance and low conflict detected"
        elif accept_score <= auto_decline_threshold:
            decision = "auto_decline"
            confidence = 1.0 - accept_score
            reasoning = "Low priority or high conflict detected"
        else:
            # Need user input or suggest alternative
            if random.random() < patterns.get("suggest_alternative_probability", 0.2):
                decision = "suggest_alternative"
                confidence = 0.6
                reasoning = "Moderate priority, suggesting alternative time"
            else:
                decision = "request_user_input"
                confidence = 0.5
                reasoning = "Unable to make autonomous decision"

        result = {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "data_considered": {
                "importance": meeting_importance,
                "conflict_level": conflict_level,
                "organizer_priority": organizer_priority
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        self.decision_history.append(result)
        return result

    def _decide_conflict_resolution(self, data: Dict[str, Any], patterns: Dict[str, float]) -> Dict[str, Any]:
        """Decide on conflict resolution"""
        conflict_severity = data.get("conflict_severity", 0.5)
        meetings_involved = data.get("meetings_involved", [])
        reschedule_options = data.get("reschedule_options", [])

        reschedule_preference = patterns.get("reschedule_preference", 0.6)

        if conflict_severity > 0.7 and reschedule_options:
            decision = "reschedule_lower_priority"
            confidence = reschedule_preference
            reasoning = "High conflict severity, rescheduling recommended"
        elif len(meetings_involved) == 2 and all(m.get("priority", 0.5) < 0.6 for m in meetings_involved):
            decision = "suggest_reschedule_both"
            confidence = 0.7
            reasoning = "Both meetings have low priority"
        else:
            decision = "escalate_to_user"
            confidence = 0.4
            reasoning = "Complex conflict requiring user judgment"

        result = {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "suggested_actions": self._generate_conflict_actions(decision, data),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.decision_history.append(result)
        return result

    def _decide_focus_time_protection(self, data: Dict[str, Any], patterns: Dict[str, float]) -> Dict[str, Any]:
        """Decide on focus time protection"""
        interruption_type = data.get("interruption_type", "meeting")
        focus_session_remaining = data.get("focus_session_remaining", 0)
        interruption_importance = data.get("interruption_importance", 0.5)

        protection_strength = patterns.get("protection_strength", 0.7)
        interruption_tolerance = patterns.get("interruption_tolerance", 0.3)

        if focus_session_remaining > 30 and interruption_importance < (1.0 - protection_strength):
            decision = "block_interruption"
            confidence = protection_strength
            reasoning = "Protecting focused work time"
        elif interruption_importance > 0.8:
            decision = "allow_interruption"
            confidence = interruption_importance
            reasoning = "High importance interruption allowed"
        else:
            decision = "defer_interruption"
            confidence = 0.6
            reasoning = "Deferring interruption to maintain focus"

        result = {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "defer_until": self._calculate_defer_time(focus_session_remaining) if decision == "defer_interruption" else None,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.decision_history.append(result)
        return result

    def _generic_decision(self, data: Dict[str, Any], patterns: Dict[str, float]) -> Dict[str, Any]:
        """Generic decision making"""
        return {
            "decision": "request_user_input",
            "confidence": 0.5,
            "reasoning": "Generic decision context, requiring user input",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _generate_conflict_actions(self, decision: str, data: Dict[str, Any]) -> List[str]:
        """Generate suggested actions for conflict resolution"""
        actions = []

        if decision == "reschedule_lower_priority":
            actions.append("Reschedule the lower priority meeting")
            actions.append("Notify affected attendees")
            actions.append("Find alternative time slots")

        elif decision == "suggest_reschedule_both":
            actions.append("Suggest rescheduling both conflicting meetings")
            actions.append("Propose alternative times for each meeting")
            actions.append("Coordinate with all attendees")

        return actions

    def _calculate_defer_time(self, remaining_minutes: int) -> str:
        """Calculate when to defer an interruption"""
        defer_minutes = min(remaining_minutes + 15, 120)  # Max 2 hour defer
        defer_time = datetime.utcnow() + timedelta(minutes=defer_minutes)
        return defer_time.isoformat()

    def learn_from_feedback(self, decision_id: str, feedback: Dict[str, Any]):
        """Learn from user feedback on decisions"""
        # Find the decision in history
        decision = next(
            (d for d in self.decision_history if d.get("id") == decision_id),
            None
        )

        if not decision:
            return

        user_agreed = feedback.get("user_agreed", False)
        user_action = feedback.get("user_action")

        # Simple learning: adjust patterns based on feedback
        if not user_agreed and decision.get("decision") == "auto_accept":
            # If user disagreed with auto-accept, lower acceptance threshold
            context = DecisionContext.MEETING_INVITATION
            if context in self.personality.decision_patterns:
                current_threshold = self.personality.decision_patterns[context].get("auto_accept_threshold", 0.7)
                self.personality.decision_patterns[context]["auto_accept_threshold"] = max(0.1, current_threshold - 0.05)

        logger.info(f"Learning from feedback for decision {decision_id}: agreed={user_agreed}")

    def get_decision_stats(self) -> Dict[str, Any]:
        """Get statistics about decision making"""
        if not self.decision_history:
            return {"total_decisions": 0}

        decisions = [d["decision"] for d in self.decision_history]
        confidences = [d["confidence"] for d in self.decision_history]

        return {
            "total_decisions": len(self.decision_history),
            "average_confidence": sum(confidences) / len(confidences),
            "decision_breakdown": {
                decision: decisions.count(decision) for decision in set(decisions)
            },
            "recent_decisions": self.decision_history[-10:]  # Last 10 decisions
        }