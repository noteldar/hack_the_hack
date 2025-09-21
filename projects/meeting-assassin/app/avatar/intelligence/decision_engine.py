"""
Decision Engine - Intelligent decision-making for meeting participation
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from openai import AsyncOpenAI
import numpy as np

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses the avatar can make"""
    ANSWER = "answer"
    CLARIFICATION = "clarification"
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    SUMMARY = "summary"
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    REDIRECT = "redirect"


class ResponsePriority(Enum):
    """Priority levels for responses"""
    CRITICAL = 1  # Must respond immediately
    HIGH = 2      # Should respond soon
    MEDIUM = 3    # Can respond when appropriate
    LOW = 4       # Optional response
    NONE = 5      # Should not respond


@dataclass
class DecisionContext:
    """Context for making a decision"""
    trigger: str
    meeting_context: Dict[str, Any]
    recent_transcript: List[Dict[str, Any]]
    personality_traits: Dict[str, float]
    knowledge_base: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class ResponseDecision:
    """A decision about how to respond"""
    should_respond: bool
    response_type: Optional[ResponseType]
    priority: ResponsePriority
    confidence: float
    reasoning: str
    suggested_response: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)
    timing_delay: float = 0.0  # Seconds to wait before responding


class DecisionEngine:
    """
    Intelligent decision-making engine for avatar responses
    """

    def __init__(self, openai_client: AsyncOpenAI, personality_system: Any):
        """Initialize decision engine"""
        self.openai_client = openai_client
        self.personality_system = personality_system

        # Decision history
        self.decision_history: List[ResponseDecision] = []

        # Response templates
        self.response_templates = self._initialize_templates()

        # Decision rules
        self.decision_rules = self._initialize_rules()

    def _initialize_templates(self) -> Dict[ResponseType, List[str]]:
        """Initialize response templates"""
        return {
            ResponseType.AGREEMENT: [
                "I agree with that approach.",
                "That makes sense to me.",
                "I'm on board with this.",
                "That aligns with our goals."
            ],
            ResponseType.DISAGREEMENT: [
                "I have a different perspective on this.",
                "I'm not sure that's the best approach.",
                "Let me offer an alternative view.",
                "I have some concerns about that."
            ],
            ResponseType.CLARIFICATION: [
                "Could you elaborate on that?",
                "What do you mean by {topic}?",
                "Can you provide more context?",
                "I want to make sure I understand correctly."
            ],
            ResponseType.SUGGESTION: [
                "What if we {suggestion}?",
                "I'd suggest {suggestion}.",
                "Have we considered {suggestion}?",
                "Another approach could be {suggestion}."
            ]
        }

    def _initialize_rules(self) -> List[Dict[str, Any]]:
        """Initialize decision rules"""
        return [
            {
                "condition": "direct_mention",
                "priority": ResponsePriority.CRITICAL,
                "response_type": ResponseType.ANSWER
            },
            {
                "condition": "direct_question",
                "priority": ResponsePriority.HIGH,
                "response_type": ResponseType.ANSWER
            },
            {
                "condition": "expertise_match",
                "priority": ResponsePriority.MEDIUM,
                "response_type": ResponseType.SUGGESTION
            },
            {
                "condition": "decision_point",
                "priority": ResponsePriority.HIGH,
                "response_type": ResponseType.DECISION
            },
            {
                "condition": "confusion_detected",
                "priority": ResponsePriority.MEDIUM,
                "response_type": ResponseType.CLARIFICATION
            }
        ]

    async def make_decision(self, context: DecisionContext) -> ResponseDecision:
        """Make a decision about whether and how to respond"""
        try:
            # Analyze the context
            analysis = await self._analyze_context(context)

            # Check decision rules
            rule_decision = self._apply_rules(analysis, context)

            # Get personality-based decision
            personality_decision = self._apply_personality(analysis, context)

            # Combine decisions
            final_decision = self._combine_decisions(
                rule_decision,
                personality_decision,
                analysis
            )

            # Generate suggested response if needed
            if final_decision.should_respond:
                final_decision.suggested_response = await self._generate_response(
                    context,
                    final_decision.response_type
                )

            # Record decision
            self.decision_history.append(final_decision)

            return final_decision

        except Exception as e:
            logger.error(f"Decision error: {e}")
            return ResponseDecision(
                should_respond=False,
                response_type=None,
                priority=ResponsePriority.NONE,
                confidence=0.0,
                reasoning="Error in decision making"
            )

    async def _analyze_context(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze the context for decision making"""
        analysis = {
            "is_direct_mention": False,
            "is_question": False,
            "topic_relevance": 0.0,
            "expertise_match": 0.0,
            "urgency": 0.0,
            "sentiment": "neutral",
            "decision_needed": False,
            "clarification_needed": False
        }

        # Check for direct mention
        name = self.personality_system.profile.name.lower()
        trigger_lower = context.trigger.lower()
        analysis["is_direct_mention"] = name in trigger_lower

        # Check if it's a question
        analysis["is_question"] = "?" in context.trigger

        # Analyze topic relevance
        analysis["topic_relevance"] = await self.assess_relevance(
            context.trigger,
            context.meeting_context.get("topics", [])
        )

        # Check expertise match
        expertise = self.personality_system.profile.expertise_areas
        analysis["expertise_match"] = self._calculate_expertise_match(
            context.trigger,
            expertise
        )

        # Assess urgency
        urgency_keywords = ["urgent", "asap", "immediately", "critical", "now"]
        analysis["urgency"] = any(word in trigger_lower for word in urgency_keywords)

        # Check for decision points
        decision_keywords = ["decide", "choose", "vote", "agree", "approve"]
        analysis["decision_needed"] = any(word in trigger_lower for word in decision_keywords)

        # Check for confusion
        confusion_keywords = ["confused", "unclear", "don't understand", "what do you mean"]
        analysis["clarification_needed"] = any(word in trigger_lower for word in confusion_keywords)

        return analysis

    async def assess_relevance(self, text: str, topics: List[str]) -> float:
        """Assess relevance of text to topics"""
        if not topics:
            return 0.5

        # Simple keyword matching (would use embeddings in production)
        text_lower = text.lower()
        matches = sum(1 for topic in topics if topic.lower() in text_lower)
        return min(1.0, matches / len(topics)) if topics else 0.0

    def _calculate_expertise_match(self, text: str, expertise_areas: List[str]) -> float:
        """Calculate how well text matches expertise areas"""
        if not expertise_areas:
            return 0.0

        text_lower = text.lower()
        matches = sum(1 for area in expertise_areas if area.lower() in text_lower)
        return min(1.0, matches / len(expertise_areas))

    def _apply_rules(
        self,
        analysis: Dict[str, Any],
        context: DecisionContext
    ) -> ResponseDecision:
        """Apply decision rules"""
        # Direct mention - highest priority
        if analysis["is_direct_mention"]:
            return ResponseDecision(
                should_respond=True,
                response_type=ResponseType.ANSWER,
                priority=ResponsePriority.CRITICAL,
                confidence=0.9,
                reasoning="Directly mentioned in conversation"
            )

        # Direct question with high relevance
        if analysis["is_question"] and analysis["topic_relevance"] > 0.6:
            return ResponseDecision(
                should_respond=True,
                response_type=ResponseType.ANSWER,
                priority=ResponsePriority.HIGH,
                confidence=0.8,
                reasoning="Relevant question asked"
            )

        # Expertise match
        if analysis["expertise_match"] > 0.7:
            return ResponseDecision(
                should_respond=True,
                response_type=ResponseType.SUGGESTION,
                priority=ResponsePriority.MEDIUM,
                confidence=0.7,
                reasoning="Topic matches expertise"
            )

        # Decision needed
        if analysis["decision_needed"]:
            return ResponseDecision(
                should_respond=True,
                response_type=ResponseType.DECISION,
                priority=ResponsePriority.HIGH,
                confidence=0.7,
                reasoning="Decision point reached"
            )

        # Default: don't respond
        return ResponseDecision(
            should_respond=False,
            response_type=None,
            priority=ResponsePriority.NONE,
            confidence=0.5,
            reasoning="No clear trigger for response"
        )

    def _apply_personality(
        self,
        analysis: Dict[str, Any],
        context: DecisionContext
    ) -> ResponseDecision:
        """Apply personality traits to decision"""
        personality = context.personality_traits

        # High participation frequency - more likely to respond
        participation = personality.get("participation_frequency", 0.5)
        threshold = 1.0 - participation

        # Calculate response probability
        response_score = (
            analysis["topic_relevance"] * 0.3 +
            analysis["expertise_match"] * 0.3 +
            (1.0 if analysis["is_question"] else 0.0) * 0.2 +
            (1.0 if analysis["decision_needed"] else 0.0) * 0.2
        )

        should_respond = response_score > threshold

        # Determine response type based on personality
        if should_respond:
            if personality.get("assertiveness", 0.5) > 0.7:
                response_type = ResponseType.DECISION
            elif personality.get("question_asking_tendency", 0.5) > 0.6:
                response_type = ResponseType.QUESTION
            elif personality.get("agreement_tendency", 0.5) > 0.6:
                response_type = ResponseType.AGREEMENT
            else:
                response_type = ResponseType.SUGGESTION

            # Calculate timing based on assertiveness
            timing_delay = 2.0 - (personality.get("assertiveness", 0.5) * 1.5)

            return ResponseDecision(
                should_respond=True,
                response_type=response_type,
                priority=ResponsePriority.MEDIUM,
                confidence=response_score,
                reasoning="Personality-driven response",
                timing_delay=timing_delay
            )

        return ResponseDecision(
            should_respond=False,
            response_type=None,
            priority=ResponsePriority.NONE,
            confidence=response_score,
            reasoning="Personality suggests not responding"
        )

    def _combine_decisions(
        self,
        rule_decision: ResponseDecision,
        personality_decision: ResponseDecision,
        analysis: Dict[str, Any]
    ) -> ResponseDecision:
        """Combine rule-based and personality-based decisions"""
        # Rules take precedence for critical responses
        if rule_decision.priority == ResponsePriority.CRITICAL:
            return rule_decision

        # Combine confidences
        combined_confidence = (
            rule_decision.confidence * 0.6 +
            personality_decision.confidence * 0.4
        )

        # Decide based on combined confidence
        if combined_confidence > 0.6:
            # Use rule-based response type if confidence is high
            if rule_decision.confidence > personality_decision.confidence:
                return rule_decision
            else:
                return personality_decision

        return ResponseDecision(
            should_respond=False,
            response_type=None,
            priority=ResponsePriority.NONE,
            confidence=combined_confidence,
            reasoning="Combined confidence too low"
        )

    async def _generate_response(
        self,
        context: DecisionContext,
        response_type: ResponseType
    ) -> str:
        """Generate appropriate response based on type"""
        try:
            # Build prompt
            prompt = f"""
            Generate a {response_type.value} response to: "{context.trigger}"

            Context:
            - Meeting type: {context.meeting_context.get('type', 'general')}
            - Your role: {self.personality_system.profile.role}
            - Your expertise: {', '.join(self.personality_system.profile.expertise_areas[:3])}

            Recent conversation:
            {self._format_transcript(context.recent_transcript[-3:])}

            Guidelines:
            - Be concise and professional
            - Match the communication style: {self.personality_system.profile.communication_style.value}
            - Stay relevant to the discussion
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.personality_system.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=self.personality_system.profile.creativity_level
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            # Fallback to template
            return self._get_template_response(response_type)

    def _get_template_response(self, response_type: ResponseType) -> str:
        """Get a template response"""
        templates = self.response_templates.get(response_type, [])
        if templates:
            return np.random.choice(templates)
        return "I understand."

    def _format_transcript(self, transcript: List[Dict[str, Any]]) -> str:
        """Format transcript for prompt"""
        formatted = []
        for entry in transcript:
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("text", "")
            formatted.append(f"{speaker}: {text}")
        return "\n".join(formatted)

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get decision history"""
        return [
            {
                "should_respond": d.should_respond,
                "response_type": d.response_type.value if d.response_type else None,
                "priority": d.priority.value,
                "confidence": d.confidence,
                "reasoning": d.reasoning
            }
            for d in self.decision_history[-10:]  # Last 10 decisions
        ]

    def should_interrupt(self, current_speaker: str, urgency: float) -> bool:
        """Determine if avatar should interrupt current speaker"""
        # High assertiveness and urgency allow interruption
        assertiveness = self.personality_system.profile.assertiveness

        if assertiveness > 0.8 and urgency > 0.8:
            return True
        elif assertiveness > 0.6 and urgency > 0.9:
            return True
        else:
            return False

    async def evaluate_response_quality(
        self,
        response: str,
        context: DecisionContext
    ) -> float:
        """Evaluate quality of a response"""
        try:
            prompt = f"""
            Evaluate this response on a scale of 0-1:
            Response: "{response}"
            Context: "{context.trigger}"

            Criteria:
            - Relevance
            - Professionalism
            - Clarity
            - Value added

            Return only a number between 0 and 1.
            """

            result = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a response evaluator. Return only a number."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )

            return float(result.choices[0].message.content.strip())

        except Exception as e:
            logger.error(f"Response evaluation error: {e}")
            return 0.5