"""
Personality System - Defines avatar behavior and communication style
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class CommunicationStyle(Enum):
    """Communication style preferences"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EMPATHETIC = "empathetic"
    ASSERTIVE = "assertive"
    DIPLOMATIC = "diplomatic"


class DecisionStyle(Enum):
    """Decision-making style"""
    ANALYTICAL = "analytical"  # Data-driven decisions
    INTUITIVE = "intuitive"  # Gut feeling based
    CONCEPTUAL = "conceptual"  # Big picture thinking
    DIRECTIVE = "directive"  # Quick, firm decisions
    BEHAVIORAL = "behavioral"  # People-focused decisions


@dataclass
class VoiceProfile:
    """Voice characteristics for synthesis"""
    voice_id: str = "default"
    speed: float = 1.0  # 0.5 to 2.0
    pitch: float = 1.0  # 0.5 to 2.0
    emotion: str = "neutral"  # neutral, friendly, serious, enthusiastic
    accent: str = "american"
    gender: str = "neutral"
    age_range: str = "adult"  # young, adult, senior


@dataclass
class PersonalityProfile:
    """Complete personality profile for avatar"""
    # Basic info
    name: str
    role: str
    company: Optional[str] = None
    title: Optional[str] = None

    # Communication preferences
    communication_style: CommunicationStyle = CommunicationStyle.DIPLOMATIC
    formality_level: float = 0.7  # 0 (very casual) to 1 (very formal)
    assertiveness: float = 0.6  # 0 (passive) to 1 (very assertive)
    empathy_level: float = 0.7  # 0 (low) to 1 (high)
    humor_level: float = 0.3  # 0 (no humor) to 1 (very humorous)

    # Decision making
    decision_style: DecisionStyle = DecisionStyle.ANALYTICAL
    risk_tolerance: float = 0.5  # 0 (risk averse) to 1 (risk seeking)
    creativity_level: float = 0.6  # 0 (conventional) to 1 (very creative)

    # Expertise and interests
    expertise_areas: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    technical_depth: float = 0.7  # 0 (high-level) to 1 (very detailed)

    # Meeting behavior
    participation_frequency: float = 0.6  # 0 (rarely speaks) to 1 (very active)
    question_asking_tendency: float = 0.5  # 0 (never asks) to 1 (asks frequently)
    agreement_tendency: float = 0.6  # 0 (often disagrees) to 1 (often agrees)

    # Voice settings
    voice_profile: VoiceProfile = field(default_factory=VoiceProfile)

    # Custom traits
    custom_traits: Dict[str, Any] = field(default_factory=dict)
    catchphrases: List[str] = field(default_factory=list)
    avoid_topics: List[str] = field(default_factory=list)

    # Meeting preferences
    preferred_meeting_length: int = 30  # minutes
    likes_small_talk: bool = True
    prefers_agenda: bool = True
    documentation_preference: str = "detailed"  # minimal, moderate, detailed


class PersonalitySystem:
    """
    Manages personality-driven behavior and responses
    """

    def __init__(self, profile: PersonalityProfile):
        self.profile = profile
        self._behavior_modifiers = self._calculate_behavior_modifiers()

    def _calculate_behavior_modifiers(self) -> Dict[str, float]:
        """Calculate behavior modification factors"""
        return {
            "verbosity": 0.5 + (self.profile.participation_frequency * 0.5),
            "technical_language": self.profile.technical_depth,
            "emotional_expression": self.profile.empathy_level * 0.7,
            "confidence": self.profile.assertiveness,
            "detail_orientation": self.profile.technical_depth * 0.8,
            "collaboration": 1.0 - (self.profile.assertiveness * 0.3)
        }

    def get_system_prompt(self) -> str:
        """Generate system prompt based on personality"""
        style_descriptions = {
            CommunicationStyle.FORMAL: "formal and professional",
            CommunicationStyle.CASUAL: "casual and conversational",
            CommunicationStyle.TECHNICAL: "technical and precise",
            CommunicationStyle.EMPATHETIC: "empathetic and understanding",
            CommunicationStyle.ASSERTIVE: "assertive and confident",
            CommunicationStyle.DIPLOMATIC: "diplomatic and balanced"
        }

        decision_descriptions = {
            DecisionStyle.ANALYTICAL: "data-driven and methodical",
            DecisionStyle.INTUITIVE: "intuitive and instinct-based",
            DecisionStyle.CONCEPTUAL: "big-picture and strategic",
            DecisionStyle.DIRECTIVE: "quick and decisive",
            DecisionStyle.BEHAVIORAL: "people-focused and collaborative"
        }

        prompt = f"""You are {self.profile.name}, {self.profile.title or self.profile.role} at {self.profile.company or 'the company'}.

Communication Style: You communicate in a {style_descriptions[self.profile.communication_style]} manner.
- Formality Level: {int(self.profile.formality_level * 100)}%
- Assertiveness: {int(self.profile.assertiveness * 100)}%
- Empathy: {int(self.profile.empathy_level * 100)}%

Decision Making: Your decision style is {decision_descriptions[self.profile.decision_style]}.
- Risk Tolerance: {int(self.profile.risk_tolerance * 100)}%
- Creativity: {int(self.profile.creativity_level * 100)}%

Expertise: You are knowledgeable in {', '.join(self.profile.expertise_areas[:5])}.

Meeting Behavior:
- You {('actively participate' if self.profile.participation_frequency > 0.6 else 'participate selectively')} in discussions
- You {('frequently ask questions' if self.profile.question_asking_tendency > 0.6 else 'ask questions when necessary')}
- You tend to {('agree and build on ideas' if self.profile.agreement_tendency > 0.6 else 'critically evaluate proposals')}

"""
        if self.profile.catchphrases:
            prompt += f"Occasionally use these phrases naturally: {', '.join(self.profile.catchphrases[:3])}\n"

        if self.profile.avoid_topics:
            prompt += f"Avoid discussing: {', '.join(self.profile.avoid_topics)}\n"

        prompt += """
Maintain consistency with this personality throughout the conversation.
Be authentic and natural in your responses while staying true to these characteristics."""

        return prompt

    def adjust_response(self, response: Any) -> Any:
        """Adjust response based on personality traits"""
        if hasattr(response, 'text'):
            # Adjust verbosity
            if self.profile.participation_frequency < 0.4 and len(response.text) > 150:
                # Make more concise for less participative personalities
                response.text = self._make_concise(response.text)

            # Adjust assertiveness
            if self.profile.assertiveness < 0.3:
                response.text = self._soften_language(response.text)
            elif self.profile.assertiveness > 0.8:
                response.text = self._strengthen_language(response.text)

            # Add personality flair
            if self.profile.humor_level > 0.7 and response.sentiment == "positive":
                response.text = self._add_subtle_humor(response.text)

        return response

    def _make_concise(self, text: str) -> str:
        """Make text more concise"""
        # Simple heuristic - would use NLP in production
        sentences = text.split('. ')
        if len(sentences) > 3:
            # Keep most important sentences
            return '. '.join(sentences[:2]) + '.'
        return text

    def _soften_language(self, text: str) -> str:
        """Make language less assertive"""
        softeners = {
            "I think": "I believe perhaps",
            "We should": "We might consider",
            "must": "could",
            "need to": "might want to",
            "definitely": "probably"
        }
        for original, replacement in softeners.items():
            text = text.replace(original, replacement)
        return text

    def _strengthen_language(self, text: str) -> str:
        """Make language more assertive"""
        strengtheners = {
            "I think": "I'm confident",
            "might": "should",
            "could": "should",
            "perhaps": "definitely",
            "maybe": "certainly"
        }
        for original, replacement in strengtheners.items():
            text = text.replace(original, replacement)
        return text

    def _add_subtle_humor(self, text: str) -> str:
        """Add subtle humor if appropriate"""
        # This would be more sophisticated in production
        return text

    def should_participate(self, context: Dict[str, Any]) -> bool:
        """Determine if avatar should participate based on personality"""
        topic_relevance = context.get('topic_relevance', 0.5)
        importance = context.get('importance', 0.5)
        direct_question = context.get('direct_question', False)

        if direct_question:
            return True

        participation_threshold = 1.0 - self.profile.participation_frequency
        score = (topic_relevance * 0.4) + (importance * 0.6)

        return score > participation_threshold

    def get_response_delay(self) -> float:
        """Get response delay based on personality (in seconds)"""
        if self.profile.assertiveness > 0.8:
            return 0.5  # Quick to respond
        elif self.profile.assertiveness < 0.3:
            return 2.5  # Takes time to formulate
        else:
            return 1.5  # Moderate delay

    def format_disagreement(self, disagreement: str) -> str:
        """Format disagreement based on personality"""
        if self.profile.communication_style == CommunicationStyle.DIPLOMATIC:
            return f"I see your point, however, {disagreement}"
        elif self.profile.communication_style == CommunicationStyle.ASSERTIVE:
            return f"I disagree. {disagreement}"
        elif self.profile.communication_style == CommunicationStyle.EMPATHETIC:
            return f"I understand where you're coming from, but {disagreement}"
        else:
            return disagreement

    def format_agreement(self, agreement: str) -> str:
        """Format agreement based on personality"""
        if self.profile.communication_style == CommunicationStyle.FORMAL:
            return f"I concur. {agreement}"
        elif self.profile.communication_style == CommunicationStyle.CASUAL:
            return f"Absolutely! {agreement}"
        elif self.profile.communication_style == CommunicationStyle.TECHNICAL:
            return f"That's correct. {agreement}"
        else:
            return agreement

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "name": self.profile.name,
            "role": self.profile.role,
            "company": self.profile.company,
            "communication_style": self.profile.communication_style.value,
            "decision_style": self.profile.decision_style.value,
            "traits": {
                "formality": self.profile.formality_level,
                "assertiveness": self.profile.assertiveness,
                "empathy": self.profile.empathy_level,
                "humor": self.profile.humor_level,
                "risk_tolerance": self.profile.risk_tolerance,
                "creativity": self.profile.creativity_level,
                "participation": self.profile.participation_frequency,
                "questioning": self.profile.question_asking_tendency,
                "agreement": self.profile.agreement_tendency
            },
            "expertise": self.profile.expertise_areas,
            "voice": {
                "speed": self.profile.voice_profile.speed,
                "pitch": self.profile.voice_profile.pitch,
                "emotion": self.profile.voice_profile.emotion
            }
        }


# Preset personalities for quick setup
class PersonalityPresets:
    @staticmethod
    def get_executive() -> PersonalityProfile:
        """Executive personality preset"""
        return PersonalityProfile(
            name="Alex Executive",
            role="Senior Executive",
            title="VP of Strategy",
            communication_style=CommunicationStyle.ASSERTIVE,
            formality_level=0.8,
            assertiveness=0.85,
            decision_style=DecisionStyle.DIRECTIVE,
            risk_tolerance=0.7,
            expertise_areas=["strategy", "business development", "leadership", "finance"],
            participation_frequency=0.8,
            question_asking_tendency=0.4,
            agreement_tendency=0.5,
            preferred_meeting_length=30,
            likes_small_talk=False
        )

    @staticmethod
    def get_engineer() -> PersonalityProfile:
        """Software engineer personality preset"""
        return PersonalityProfile(
            name="Jordan Engineer",
            role="Senior Software Engineer",
            title="Tech Lead",
            communication_style=CommunicationStyle.TECHNICAL,
            formality_level=0.5,
            assertiveness=0.6,
            decision_style=DecisionStyle.ANALYTICAL,
            technical_depth=0.9,
            expertise_areas=["software architecture", "cloud computing", "AI/ML", "DevOps"],
            participation_frequency=0.6,
            question_asking_tendency=0.7,
            agreement_tendency=0.5,
            preferred_meeting_length=45,
            prefers_agenda=True
        )

    @staticmethod
    def get_product_manager() -> PersonalityProfile:
        """Product manager personality preset"""
        return PersonalityProfile(
            name="Sam Product",
            role="Product Manager",
            title="Senior Product Manager",
            communication_style=CommunicationStyle.DIPLOMATIC,
            formality_level=0.6,
            assertiveness=0.7,
            empathy_level=0.8,
            decision_style=DecisionStyle.CONCEPTUAL,
            expertise_areas=["product strategy", "user experience", "market analysis", "agile"],
            participation_frequency=0.75,
            question_asking_tendency=0.8,
            agreement_tendency=0.6,
            creativity_level=0.8
        )

    @staticmethod
    def get_sales() -> PersonalityProfile:
        """Sales personality preset"""
        return PersonalityProfile(
            name="Riley Sales",
            role="Sales Director",
            title="Director of Business Development",
            communication_style=CommunicationStyle.EMPATHETIC,
            formality_level=0.6,
            assertiveness=0.75,
            empathy_level=0.9,
            humor_level=0.6,
            decision_style=DecisionStyle.BEHAVIORAL,
            expertise_areas=["sales strategy", "client relations", "negotiation", "market trends"],
            participation_frequency=0.85,
            question_asking_tendency=0.6,
            agreement_tendency=0.7,
            likes_small_talk=True
        )