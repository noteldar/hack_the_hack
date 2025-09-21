"""
Enhanced Personality-Based Decision Engine with LLM Integration
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
import numpy as np
from app.ai.llm_analyzer import LLMAnalyzer, MeetingInsight, AnalysisDepth

logger = logging.getLogger(__name__)


class PersonalityType(Enum):
    """Enhanced AI personality types"""
    PROFESSIONAL = "professional"  # Balanced, formal approach
    ASSERTIVE = "assertive"  # Direct, time-protective
    COLLABORATIVE = "collaborative"  # Team-focused, inclusive
    PROTECTIVE = "protective"  # Guards user's time aggressively
    EFFICIENT = "efficient"  # Optimization-focused


@dataclass
class PersonalityDecision:
    """Decision made by a personality"""
    personality_type: PersonalityType
    decision: str  # accept, decline, reschedule, delegate, request_info
    confidence: float  # 0.0 to 1.0
    reasoning: str
    natural_explanation: str
    suggested_actions: List[str]
    alternative_options: List[Dict[str, Any]]
    emotional_tone: str  # professional, friendly, assertive, empathetic
    response_template: str  # Email/message template
    learning_factors: Dict[str, float]  # Factors that influenced decision
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'personality_type': self.personality_type.value,
            'timestamp': self.timestamp.isoformat()
        }


class EnhancedPersonalityEngine:
    """Advanced personality-based decision engine with LLM integration"""

    # Personality characteristics with enhanced traits
    PERSONALITY_PROFILES = {
        PersonalityType.PROFESSIONAL: {
            "traits": {
                "assertiveness": 0.6,
                "collaboration": 0.7,
                "efficiency": 0.8,
                "protection": 0.5,
                "adaptability": 0.6,
                "communication": 0.7,
                "decision_speed": 0.6,
                "risk_tolerance": 0.4,
                "empathy": 0.7,
                "formality": 0.9
            },
            "decision_weights": {
                "importance": 0.35,
                "urgency": 0.25,
                "strategic_value": 0.20,
                "relationship": 0.10,
                "workload": 0.10
            },
            "communication_style": {
                "greeting": "Thank you for the meeting invitation.",
                "decline_phrase": "I regret that I cannot attend",
                "reschedule_phrase": "Would it be possible to reschedule",
                "closing": "Best regards",
                "tone": "formal and courteous"
            },
            "thresholds": {
                "auto_accept": 0.75,
                "auto_decline": 0.35,
                "delegate": 0.50,
                "reschedule": 0.55
            }
        },
        PersonalityType.ASSERTIVE: {
            "traits": {
                "assertiveness": 0.95,
                "collaboration": 0.4,
                "efficiency": 0.9,
                "protection": 0.85,
                "adaptability": 0.3,
                "communication": 0.6,
                "decision_speed": 0.9,
                "risk_tolerance": 0.7,
                "empathy": 0.4,
                "formality": 0.5
            },
            "decision_weights": {
                "importance": 0.40,
                "urgency": 0.20,
                "strategic_value": 0.25,
                "relationship": 0.05,
                "workload": 0.10
            },
            "communication_style": {
                "greeting": "Regarding your meeting request:",
                "decline_phrase": "This meeting doesn't align with current priorities",
                "reschedule_phrase": "This needs to be rescheduled to",
                "closing": "Thanks",
                "tone": "direct and decisive"
            },
            "thresholds": {
                "auto_accept": 0.85,
                "auto_decline": 0.25,
                "delegate": 0.40,
                "reschedule": 0.45
            }
        },
        PersonalityType.COLLABORATIVE: {
            "traits": {
                "assertiveness": 0.3,
                "collaboration": 0.95,
                "efficiency": 0.6,
                "protection": 0.3,
                "adaptability": 0.85,
                "communication": 0.9,
                "decision_speed": 0.4,
                "risk_tolerance": 0.7,
                "empathy": 0.95,
                "formality": 0.6
            },
            "decision_weights": {
                "importance": 0.25,
                "urgency": 0.20,
                "strategic_value": 0.15,
                "relationship": 0.25,
                "workload": 0.15
            },
            "communication_style": {
                "greeting": "Thanks so much for including me!",
                "decline_phrase": "I'm so sorry, but I won't be able to make it",
                "reschedule_phrase": "Could we find another time that works for everyone",
                "closing": "Looking forward to connecting",
                "tone": "warm and inclusive"
            },
            "thresholds": {
                "auto_accept": 0.60,
                "auto_decline": 0.45,
                "delegate": 0.65,
                "reschedule": 0.70
            }
        },
        PersonalityType.PROTECTIVE: {
            "traits": {
                "assertiveness": 0.8,
                "collaboration": 0.5,
                "efficiency": 0.7,
                "protection": 0.95,
                "adaptability": 0.4,
                "communication": 0.6,
                "decision_speed": 0.7,
                "risk_tolerance": 0.2,
                "empathy": 0.6,
                "formality": 0.7
            },
            "decision_weights": {
                "importance": 0.30,
                "urgency": 0.30,
                "strategic_value": 0.20,
                "relationship": 0.05,
                "workload": 0.15
            },
            "communication_style": {
                "greeting": "After reviewing your meeting request:",
                "decline_phrase": "This conflicts with protected focus time",
                "reschedule_phrase": "This can be moved to a less critical time slot",
                "closing": "Regards",
                "tone": "protective and boundary-setting"
            },
            "thresholds": {
                "auto_accept": 0.80,
                "auto_decline": 0.30,
                "delegate": 0.55,
                "reschedule": 0.50
            }
        },
        PersonalityType.EFFICIENT: {
            "traits": {
                "assertiveness": 0.7,
                "collaboration": 0.6,
                "efficiency": 0.99,
                "protection": 0.6,
                "adaptability": 0.7,
                "communication": 0.5,
                "decision_speed": 0.95,
                "risk_tolerance": 0.5,
                "empathy": 0.5,
                "formality": 0.6
            },
            "decision_weights": {
                "importance": 0.25,
                "urgency": 0.25,
                "strategic_value": 0.30,
                "relationship": 0.05,
                "workload": 0.15
            },
            "communication_style": {
                "greeting": "Re: Meeting request",
                "decline_phrase": "Not optimal use of time - declining",
                "reschedule_phrase": "Proposing shorter/async alternative",
                "closing": "-",
                "tone": "brief and efficiency-focused"
            },
            "thresholds": {
                "auto_accept": 0.70,
                "auto_decline": 0.35,
                "delegate": 0.45,
                "reschedule": 0.60
            }
        }
    }

    def __init__(self, llm_analyzer: Optional[LLMAnalyzer] = None):
        self.llm_analyzer = llm_analyzer or LLMAnalyzer()
        self.decision_history: Dict[PersonalityType, List[PersonalityDecision]] = {
            p: [] for p in PersonalityType
        }
        self.learning_cache = {}
        self.user_feedback_weights = self._initialize_feedback_weights()

    def _initialize_feedback_weights(self) -> Dict[str, float]:
        """Initialize feedback learning weights"""
        return {
            "user_acceptance_rate": 1.0,
            "decision_speed": 1.0,
            "meeting_effectiveness": 1.0,
            "time_saved": 1.0,
            "relationship_impact": 1.0
        }

    async def make_personality_decision(
        self,
        personality_type: PersonalityType,
        meeting_data: Dict[str, Any],
        meeting_insight: MeetingInsight,
        user_context: Optional[Dict[str, Any]] = None
    ) -> PersonalityDecision:
        """Make a decision based on specific personality"""

        profile = self.PERSONALITY_PROFILES[personality_type]

        # Calculate decision scores
        decision_scores = await self._calculate_decision_scores(
            profile,
            meeting_data,
            meeting_insight,
            user_context
        )

        # Determine primary decision
        decision = self._determine_decision(decision_scores, profile["thresholds"])

        # Generate natural language explanation
        natural_explanation = await self._generate_personality_explanation(
            personality_type,
            decision,
            meeting_data,
            meeting_insight,
            decision_scores
        )

        # Create response template
        response_template = self._create_response_template(
            personality_type,
            decision,
            meeting_data,
            natural_explanation
        )

        # Generate alternative options
        alternatives = self._generate_alternatives(
            decision,
            meeting_data,
            meeting_insight,
            profile
        )

        # Determine suggested actions
        suggested_actions = self._determine_suggested_actions(
            decision,
            meeting_insight,
            personality_type
        )

        # Calculate learning factors
        learning_factors = self._calculate_learning_factors(
            decision_scores,
            meeting_insight,
            user_context
        )

        # Create decision object
        personality_decision = PersonalityDecision(
            personality_type=personality_type,
            decision=decision,
            confidence=decision_scores["confidence"],
            reasoning=self._generate_reasoning(decision_scores, meeting_insight),
            natural_explanation=natural_explanation,
            suggested_actions=suggested_actions,
            alternative_options=alternatives,
            emotional_tone=profile["communication_style"]["tone"],
            response_template=response_template,
            learning_factors=learning_factors,
            timestamp=datetime.utcnow()
        )

        # Store in history
        self.decision_history[personality_type].append(personality_decision)

        return personality_decision

    async def get_ensemble_decision(
        self,
        meeting_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        primary_personality: Optional[PersonalityType] = None
    ) -> Dict[str, Any]:
        """Get ensemble decision from multiple personalities"""

        # Analyze meeting first
        meeting_insight = await self.llm_analyzer.analyze_meeting(
            meeting_data,
            AnalysisDepth.STANDARD,
            user_context
        )

        # Get decisions from all personalities
        decisions = {}
        for personality_type in PersonalityType:
            decision = await self.make_personality_decision(
                personality_type,
                meeting_data,
                meeting_insight,
                user_context
            )
            decisions[personality_type] = decision

        # Determine consensus or use primary personality
        if primary_personality:
            primary_decision = decisions[primary_personality]
        else:
            primary_decision = self._find_consensus(decisions)

        # Create ensemble result
        return {
            "primary_decision": primary_decision.to_dict(),
            "all_decisions": {
                p.value: d.to_dict() for p, d in decisions.items()
            },
            "meeting_insight": meeting_insight.to_dict(),
            "consensus_analysis": self._analyze_consensus(decisions),
            "recommended_action": primary_decision.decision,
            "confidence": primary_decision.confidence,
            "explanation": primary_decision.natural_explanation
        }

    async def _calculate_decision_scores(
        self,
        profile: Dict[str, Any],
        meeting_data: Dict[str, Any],
        meeting_insight: MeetingInsight,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate decision scores based on personality profile"""

        weights = profile["decision_weights"]

        # Base scores from meeting insight
        importance_score = meeting_insight.importance_score / 10.0
        urgency_score = meeting_insight.urgency_score / 10.0
        strategic_value_score = self._parse_strategic_value(meeting_insight.strategic_value)

        # Relationship score (based on organizer and attendees)
        relationship_score = self._calculate_relationship_score(
            meeting_data,
            user_context
        )

        # Workload score (based on calendar density)
        workload_score = self._calculate_workload_score(user_context)

        # Calculate weighted score
        weighted_score = (
            weights["importance"] * importance_score +
            weights["urgency"] * urgency_score +
            weights["strategic_value"] * strategic_value_score +
            weights["relationship"] * relationship_score +
            weights["workload"] * (1.0 - workload_score)  # Inverse for workload
        )

        # Adjust for personality traits
        traits = profile["traits"]

        # Assertive personalities are more likely to decline
        if traits["assertiveness"] > 0.7:
            weighted_score *= (1.0 - traits["assertiveness"] * 0.2)

        # Collaborative personalities are more likely to accept
        if traits["collaboration"] > 0.7:
            weighted_score *= (1.0 + traits["collaboration"] * 0.2)

        # Protective personalities consider focus time
        if traits["protection"] > 0.7 and self._conflicts_with_focus_time(meeting_data):
            weighted_score *= 0.5

        # Calculate confidence based on data quality
        confidence = min(0.95, meeting_insight.ai_confidence * (0.8 + weighted_score * 0.2))

        return {
            "weighted_score": weighted_score,
            "confidence": confidence,
            "importance": importance_score,
            "urgency": urgency_score,
            "strategic_value": strategic_value_score,
            "relationship": relationship_score,
            "workload": workload_score,
            "skip_probability": meeting_insight.skip_probability,
            "ai_suitable": meeting_insight.ai_attendance_suitable
        }

    def _determine_decision(
        self,
        scores: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> str:
        """Determine decision based on scores and thresholds"""

        weighted_score = scores["weighted_score"]
        skip_probability = scores["skip_probability"]
        ai_suitable = scores["ai_suitable"]

        # Check for AI attendance option
        if ai_suitable and skip_probability > 0.6:
            return "delegate_to_ai"

        # Check thresholds
        if weighted_score >= thresholds["auto_accept"]:
            return "accept"
        elif weighted_score <= thresholds["auto_decline"]:
            return "decline"
        elif weighted_score >= thresholds["reschedule"] and skip_probability > 0.4:
            return "reschedule"
        elif weighted_score >= thresholds["delegate"] and ai_suitable:
            return "delegate"
        else:
            return "request_info"

    async def _generate_personality_explanation(
        self,
        personality_type: PersonalityType,
        decision: str,
        meeting_data: Dict[str, Any],
        meeting_insight: MeetingInsight,
        decision_scores: Dict[str, float]
    ) -> str:
        """Generate personality-specific natural language explanation"""

        profile = self.PERSONALITY_PROFILES[personality_type]

        # Use LLM if available
        if self.llm_analyzer and self.llm_analyzer.client:
            prompt = f"""
            You are an AI assistant with a {personality_type.value} personality.
            Your traits: {json.dumps(profile['traits'])}
            Communication style: {profile['communication_style']['tone']}

            Explain this decision in 2-3 sentences:
            Decision: {decision}
            Meeting: {meeting_data.get('title')}
            Importance: {meeting_insight.importance_score}/10
            Your confidence: {decision_scores['confidence']:.1%}

            Write in first person, reflecting the personality style.
            """

            try:
                response = await self.llm_analyzer.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"You have a {personality_type.value} personality."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"LLM explanation generation failed: {e}")

        # Fallback to template-based explanation
        explanations = {
            PersonalityType.PROFESSIONAL: {
                "accept": f"I'll attend '{meeting_data.get('title')}' as it aligns with our strategic objectives (importance: {meeting_insight.importance_score}/10). I'll ensure we achieve the expected outcomes efficiently.",
                "decline": f"After careful consideration, I must decline '{meeting_data.get('title')}' as it doesn't align with current priorities. I suggest exploring alternative communication methods.",
                "reschedule": f"While '{meeting_data.get('title')}' is valuable, I recommend rescheduling to optimize our collective productivity. I've identified better time slots that minimize conflicts.",
                "delegate": f"I recommend delegating '{meeting_data.get('title')}' to maintain focus on higher-priority initiatives. The meeting objectives can be achieved through representation.",
                "delegate_to_ai": f"My AI assistant can effectively represent us in '{meeting_data.get('title')}', allowing me to focus on critical tasks while ensuring meeting coverage.",
                "request_info": f"I need additional context about '{meeting_data.get('title')}' to make an informed decision. Could you provide more details about the agenda and expected outcomes?"
            },
            PersonalityType.ASSERTIVE: {
                "accept": f"I'll take '{meeting_data.get('title')}' - it's worth my time (score: {meeting_insight.importance_score}/10). Let's make it count.",
                "decline": f"Declining '{meeting_data.get('title')}' - not a priority. Time is better spent on high-impact work.",
                "reschedule": f"'{meeting_data.get('title')}' needs rescheduling. Current slot isn't optimal. I've blocked better times.",
                "delegate": f"Delegating '{meeting_data.get('title')}'. Someone else can handle this while I focus on priorities.",
                "delegate_to_ai": f"AI's got '{meeting_data.get('title')}'. No need for human presence on this one.",
                "request_info": f"Need more info on '{meeting_data.get('title')}' - make the case for my time."
            },
            PersonalityType.COLLABORATIVE: {
                "accept": f"I'd love to join '{meeting_data.get('title')}' ! It's important we collaborate on this (importance: {meeting_insight.importance_score}/10). Looking forward to everyone's input!",
                "decline": f"I'm so sorry to miss '{meeting_data.get('title')}', but I have a conflict. Happy to contribute async or catch up after!",
                "reschedule": f"Could we find a better time for '{meeting_data.get('title')}'? I want to ensure everyone can participate fully!",
                "delegate": f"I think someone from my team would be perfect for '{meeting_data.get('title')}' - they'd bring great perspective!",
                "delegate_to_ai": f"My AI assistant can join '{meeting_data.get('title')}' and share notes with everyone afterward - teamwork with technology!",
                "request_info": f"I'd love to learn more about '{meeting_data.get('title')}' to see how I can best contribute! What are we hoping to achieve together?"
            },
            PersonalityType.PROTECTIVE: {
                "accept": f"Accepting '{meeting_data.get('title')}' as it's critical enough to interrupt focus time (urgency: {meeting_insight.urgency_score}/10).",
                "decline": f"Declining '{meeting_data.get('title')}' to protect scheduled focus time. This time block is non-negotiable.",
                "reschedule": f"'{meeting_data.get('title')}' must move to a non-focus time slot. Protecting deep work periods is essential.",
                "delegate": f"Delegating '{meeting_data.get('title')}' to preserve focus time. Meeting doesn't require my direct involvement.",
                "delegate_to_ai": f"AI assistant will cover '{meeting_data.get('title')}' - protecting human focus time for high-value work.",
                "request_info": f"Evaluating '{meeting_data.get('title')}' - need justification for focus time interruption."
            },
            PersonalityType.EFFICIENT: {
                "accept": f"Taking '{meeting_data.get('title')}' - ROI justified at {meeting_insight.importance_score}/10.",
                "decline": f"Declining '{meeting_data.get('title')}' - insufficient ROI. Email would be 3x faster.",
                "reschedule": f"Rescheduling '{meeting_data.get('title')}' to batch with similar meetings. 40% time savings.",
                "delegate": f"Delegating '{meeting_data.get('title')}'. More efficient use of organizational resources.",
                "delegate_to_ai": f"AI handles '{meeting_data.get('title')}'. 100% time savings, 90% effectiveness.",
                "request_info": f"Need ROI data for '{meeting_data.get('title')}'. Can't optimize without metrics."
            }
        }

        return explanations.get(personality_type, {}).get(
            decision,
            f"Making a {decision} decision on '{meeting_data.get('title')}' based on analysis."
        )

    def _create_response_template(
        self,
        personality_type: PersonalityType,
        decision: str,
        meeting_data: Dict[str, Any],
        explanation: str
    ) -> str:
        """Create email/message response template"""

        profile = self.PERSONALITY_PROFILES[personality_type]
        style = profile["communication_style"]

        if decision == "accept":
            template = f"""
{style['greeting']}

I'll be attending "{meeting_data.get('title')}".

{explanation}

{style['closing']}
"""
        elif decision == "decline":
            template = f"""
{style['greeting']}

{style['decline_phrase']} "{meeting_data.get('title')}".

{explanation}

{style['closing']}
"""
        elif decision == "reschedule":
            template = f"""
{style['greeting']}

{style['reschedule_phrase']} "{meeting_data.get('title')}"?

{explanation}

Proposed alternative times:
- [Option 1]
- [Option 2]
- [Option 3]

{style['closing']}
"""
        else:
            template = f"""
{style['greeting']}

Regarding "{meeting_data.get('title')}":

{explanation}

{style['closing']}
"""

        return template.strip()

    def _generate_alternatives(
        self,
        decision: str,
        meeting_data: Dict[str, Any],
        meeting_insight: MeetingInsight,
        profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative options"""

        alternatives = []

        if decision == "decline":
            # Suggest alternatives to declining
            if meeting_insight.ai_attendance_suitable:
                alternatives.append({
                    "option": "Send AI representative",
                    "pros": ["Stay informed", "No time commitment"],
                    "cons": ["Less personal engagement"],
                    "confidence": 0.8
                })

            alternatives.append({
                "option": "Request meeting notes",
                "pros": ["Stay informed", "Zero time commitment"],
                "cons": ["No input opportunity"],
                "confidence": 0.7
            })

            if meeting_insight.optimal_duration_minutes < 30:
                alternatives.append({
                    "option": "Suggest shorter meeting",
                    "pros": ["Participate efficiently", "Build relationships"],
                    "cons": ["Still requires time"],
                    "confidence": 0.6
                })

        elif decision == "accept":
            # Suggest optimization options
            if meeting_insight.optimal_duration_minutes < meeting_data.get("duration_minutes", 60):
                alternatives.append({
                    "option": f"Propose {meeting_insight.optimal_duration_minutes} min duration",
                    "pros": ["Save time", "More focused discussion"],
                    "cons": ["May seem pushy"],
                    "confidence": 0.7
                })

            if meeting_insight.alternative_approaches:
                for approach in meeting_insight.alternative_approaches[:2]:
                    alternatives.append({
                        "option": approach,
                        "pros": ["More efficient", "Async friendly"],
                        "cons": ["Less collaborative"],
                        "confidence": 0.6
                    })

        return alternatives

    def _determine_suggested_actions(
        self,
        decision: str,
        meeting_insight: MeetingInsight,
        personality_type: PersonalityType
    ) -> List[str]:
        """Determine suggested actions based on decision"""

        actions = []

        if decision == "accept":
            # Add preparation actions
            actions.extend(meeting_insight.required_preparation[:3])
            actions.append("Block 5 minutes before for prep")
            if meeting_insight.decision_points:
                actions.append("Review decision points in advance")

        elif decision == "decline":
            actions.append("Send polite decline message")
            if meeting_insight.ai_attendance_suitable:
                actions.append("Offer to send AI representative")
            actions.append("Request meeting summary afterwards")

        elif decision == "reschedule":
            actions.append("Propose 3 alternative time slots")
            actions.append("Explain scheduling conflict briefly")
            if personality_type == PersonalityType.EFFICIENT:
                actions.append(f"Suggest {meeting_insight.optimal_duration_minutes} min duration")

        elif decision == "delegate":
            actions.append("Identify appropriate delegate")
            actions.append("Brief delegate on context")
            actions.append("Request post-meeting summary")

        elif decision == "delegate_to_ai":
            actions.append("Configure AI with meeting context")
            actions.append("Set AI response parameters")
            actions.append("Review AI-generated summary post-meeting")

        elif decision == "request_info":
            actions.append("Ask for detailed agenda")
            actions.append("Clarify expected outcomes")
            actions.append("Understand your required contribution")

        return actions

    def _calculate_learning_factors(
        self,
        decision_scores: Dict[str, float],
        meeting_insight: MeetingInsight,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate factors for learning and adaptation"""

        factors = {
            "importance_weight": decision_scores["importance"],
            "urgency_weight": decision_scores["urgency"],
            "relationship_weight": decision_scores["relationship"],
            "workload_weight": decision_scores["workload"],
            "skip_probability": meeting_insight.skip_probability,
            "ai_suitability": 1.0 if meeting_insight.ai_attendance_suitable else 0.0,
            "confidence": decision_scores["confidence"]
        }

        # Add user context factors if available
        if user_context:
            factors["user_stress_level"] = user_context.get("stress_level", 0.5)
            factors["calendar_density"] = user_context.get("calendar_density", 0.5)
            factors["focus_time_ratio"] = user_context.get("focus_time_ratio", 0.3)

        return factors

    def _parse_strategic_value(self, strategic_value: str) -> float:
        """Parse strategic value string to score"""
        if "High" in strategic_value:
            return 0.9
        elif "Medium" in strategic_value:
            return 0.5
        elif "Low" in strategic_value:
            return 0.2
        else:
            return 0.5

    def _calculate_relationship_score(
        self,
        meeting_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate relationship importance score"""

        organizer = meeting_data.get("organizer_email", "")

        if user_context and "important_contacts" in user_context:
            important_contacts = user_context["important_contacts"]
            if organizer in important_contacts:
                return 0.9

        # Check for VIP keywords
        vip_indicators = ["ceo", "cto", "vp", "director", "client", "customer"]
        if any(indicator in organizer.lower() for indicator in vip_indicators):
            return 0.8

        # Check attendee count (smaller meetings often more important)
        attendee_count = len(meeting_data.get("attendees", []))
        if attendee_count <= 3:
            return 0.7
        elif attendee_count <= 5:
            return 0.5
        else:
            return 0.3

    def _calculate_workload_score(self, user_context: Optional[Dict[str, Any]]) -> float:
        """Calculate current workload score"""

        if not user_context:
            return 0.5

        # Use calendar density if available
        calendar_density = user_context.get("calendar_density", 0.5)

        # Adjust based on stress indicators
        stress_level = user_context.get("stress_level", 0.5)

        # Combine factors
        workload = (calendar_density * 0.7 + stress_level * 0.3)

        return min(1.0, max(0.0, workload))

    def _conflicts_with_focus_time(self, meeting_data: Dict[str, Any]) -> bool:
        """Check if meeting conflicts with typical focus time"""

        start_time = meeting_data.get("start_time")
        if not start_time:
            return False

        try:
            meeting_hour = datetime.fromisoformat(start_time).hour
            # Focus time typically 9-11 AM and 2-4 PM
            return (9 <= meeting_hour < 11) or (14 <= meeting_hour < 16)
        except:
            return False

    def _generate_reasoning(
        self,
        decision_scores: Dict[str, float],
        meeting_insight: MeetingInsight
    ) -> str:
        """Generate detailed reasoning for decision"""

        reasoning_parts = []

        # Add importance reasoning
        if decision_scores["importance"] > 0.7:
            reasoning_parts.append(f"High importance meeting ({meeting_insight.importance_score}/10)")
        elif decision_scores["importance"] < 0.3:
            reasoning_parts.append(f"Low importance meeting ({meeting_insight.importance_score}/10)")

        # Add urgency reasoning
        if decision_scores["urgency"] > 0.8:
            reasoning_parts.append("Time-sensitive matter requiring immediate attention")

        # Add strategic value
        reasoning_parts.append(f"Strategic value: {meeting_insight.strategic_value}")

        # Add skip probability
        if meeting_insight.skip_probability > 0.7:
            reasoning_parts.append("High probability this meeting can be skipped or delegated")

        # Add AI suitability
        if meeting_insight.ai_attendance_suitable:
            reasoning_parts.append("AI attendance is suitable for this meeting type")

        return ". ".join(reasoning_parts)

    def _find_consensus(
        self,
        decisions: Dict[PersonalityType, PersonalityDecision]
    ) -> PersonalityDecision:
        """Find consensus decision across personalities"""

        # Count decisions
        decision_counts = {}
        for decision in decisions.values():
            if decision.decision not in decision_counts:
                decision_counts[decision.decision] = 0
            decision_counts[decision.decision] += 1

        # Find most common decision
        most_common = max(decision_counts, key=decision_counts.get)

        # Return the decision with highest confidence for that type
        matching_decisions = [d for d in decisions.values() if d.decision == most_common]
        return max(matching_decisions, key=lambda d: d.confidence)

    def _analyze_consensus(
        self,
        decisions: Dict[PersonalityType, PersonalityDecision]
    ) -> Dict[str, Any]:
        """Analyze consensus across personalities"""

        decision_list = [d.decision for d in decisions.values()]
        confidence_list = [d.confidence for d in decisions.values()]

        # Count unique decisions
        unique_decisions = set(decision_list)

        # Calculate agreement level
        most_common_count = max(decision_list.count(d) for d in unique_decisions)
        agreement_level = most_common_count / len(decision_list)

        return {
            "agreement_level": agreement_level,
            "unique_decisions": list(unique_decisions),
            "average_confidence": np.mean(confidence_list),
            "confidence_std": np.std(confidence_list),
            "full_consensus": agreement_level == 1.0,
            "majority_decision": max(unique_decisions, key=decision_list.count),
            "dissenting_personalities": [
                p.value for p, d in decisions.items()
                if d.decision != max(unique_decisions, key=decision_list.count)
            ]
        }

    async def learn_from_feedback(
        self,
        decision_id: str,
        feedback: Dict[str, Any],
        personality_type: Optional[PersonalityType] = None
    ):
        """Learn from user feedback on decisions"""

        user_agreed = feedback.get("user_agreed", False)
        actual_outcome = feedback.get("actual_outcome")  # good, neutral, bad
        time_saved = feedback.get("time_saved", 0)  # in minutes

        # Update feedback weights
        if not user_agreed:
            self.user_feedback_weights["user_acceptance_rate"] *= 0.95
        else:
            self.user_feedback_weights["user_acceptance_rate"] *= 1.02

        if actual_outcome == "bad":
            self.user_feedback_weights["meeting_effectiveness"] *= 0.9
        elif actual_outcome == "good":
            self.user_feedback_weights["meeting_effectiveness"] *= 1.05

        # Store learning data
        self.learning_cache[decision_id] = {
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat(),
            "personality": personality_type.value if personality_type else None
        }

        # Adjust personality thresholds if specified
        if personality_type and not user_agreed:
            profile = self.PERSONALITY_PROFILES[personality_type]
            # Make more conservative
            profile["thresholds"]["auto_accept"] = min(0.95, profile["thresholds"]["auto_accept"] + 0.05)
            profile["thresholds"]["auto_decline"] = max(0.1, profile["thresholds"]["auto_decline"] - 0.05)

        logger.info(f"Learned from feedback: agreed={user_agreed}, outcome={actual_outcome}")

    def get_personality_stats(self, personality_type: PersonalityType) -> Dict[str, Any]:
        """Get statistics for a specific personality"""

        decisions = self.decision_history.get(personality_type, [])

        if not decisions:
            return {"total_decisions": 0}

        decision_types = [d.decision for d in decisions]
        confidences = [d.confidence for d in decisions]

        return {
            "total_decisions": len(decisions),
            "average_confidence": np.mean(confidences),
            "decision_breakdown": {
                decision: decision_types.count(decision)
                for decision in set(decision_types)
            },
            "recent_decisions": [d.to_dict() for d in decisions[-5:]],
            "personality_traits": self.PERSONALITY_PROFILES[personality_type]["traits"]
        }