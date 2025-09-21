"""
Main Avatar Engine - Orchestrates all meeting participation components
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
import logging
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
from openai import AsyncOpenAI
import anthropic

from .personality_system import PersonalitySystem, PersonalityProfile
from .meeting_context import MeetingContext, MeetingType
from ..transcription.whisper_engine import WhisperTranscriptionEngine
from ..synthesis.voice_synthesizer import VoiceSynthesizer
from ..intelligence.meeting_analyzer import MeetingAnalyzer
from ..intelligence.decision_engine import DecisionEngine
from ..intelligence.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class ParticipationMode(Enum):
    """Avatar participation modes"""
    ACTIVE = "active"  # Actively participates
    PASSIVE = "passive"  # Listens and takes notes
    SELECTIVE = "selective"  # Participates only when relevant
    EMERGENCY = "emergency"  # Only responds to critical items
    DEMO = "demo"  # Demo mode for hackathon


@dataclass
class AvatarResponse:
    """Structured avatar response"""
    text: str
    confidence: float
    reasoning: str
    action_items: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    should_speak: bool = True
    priority: int = 5  # 1-10 scale
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeetingState:
    """Current meeting state"""
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    current_speaker: Optional[str] = None
    topics_discussed: List[str] = field(default_factory=list)
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    sentiment_history: List[float] = field(default_factory=list)
    my_contributions: List[Dict[str, Any]] = field(default_factory=list)
    meeting_phase: str = "introduction"  # introduction, discussion, decision, conclusion
    start_time: datetime = field(default_factory=datetime.now)


class AvatarEngine:
    """
    Main AI Avatar Engine for autonomous meeting participation
    """

    def __init__(
        self,
        personality_profile: PersonalityProfile,
        openai_api_key: str,
        anthropic_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        mode: ParticipationMode = ParticipationMode.ACTIVE
    ):
        """Initialize the Avatar Engine"""
        self.personality_system = PersonalitySystem(personality_profile)
        self.mode = mode

        # AI Clients
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None

        # Core components
        self.transcription_engine = WhisperTranscriptionEngine(openai_api_key)
        self.voice_synthesizer = VoiceSynthesizer(elevenlabs_api_key)
        self.meeting_analyzer = MeetingAnalyzer(self.openai_client)
        self.decision_engine = DecisionEngine(self.openai_client, self.personality_system)
        self.knowledge_base = KnowledgeBase()

        # Meeting state
        self.current_meeting: Optional[MeetingContext] = None
        self.meeting_state = MeetingState()

        # Real-time processing
        self.audio_buffer = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.is_processing = False

        # Callbacks
        self.on_transcript_update: Optional[Callable] = None
        self.on_response_generated: Optional[Callable] = None
        self.on_action_item: Optional[Callable] = None

    async def join_meeting(self, meeting_context: MeetingContext) -> bool:
        """Join a meeting and initialize participation"""
        try:
            logger.info(f"Avatar joining meeting: {meeting_context.title}")
            self.current_meeting = meeting_context
            self.meeting_state = MeetingState()

            # Load relevant knowledge for this meeting
            await self.knowledge_base.load_context(meeting_context)

            # Start processing loops
            self.is_processing = True
            asyncio.create_task(self._transcription_loop())
            asyncio.create_task(self._response_generation_loop())
            asyncio.create_task(self._analytics_loop())

            # Generate introduction if needed
            if self.mode == ParticipationMode.ACTIVE:
                intro = await self._generate_introduction()
                if intro:
                    await self.speak(intro)

            return True

        except Exception as e:
            logger.error(f"Failed to join meeting: {e}")
            return False

    async def process_audio_stream(self, audio_data: bytes) -> None:
        """Process incoming audio stream"""
        await self.audio_buffer.put(audio_data)

    async def _transcription_loop(self) -> None:
        """Continuous transcription processing"""
        while self.is_processing:
            try:
                # Collect audio chunks
                audio_chunks = []
                deadline = asyncio.get_event_loop().time() + 0.5  # 500ms window

                while asyncio.get_event_loop().time() < deadline:
                    try:
                        chunk = await asyncio.wait_for(
                            self.audio_buffer.get(),
                            timeout=0.1
                        )
                        audio_chunks.append(chunk)
                    except asyncio.TimeoutError:
                        break

                if audio_chunks:
                    # Transcribe audio
                    audio_data = b''.join(audio_chunks)
                    transcript = await self.transcription_engine.transcribe_stream(audio_data)

                    if transcript and transcript.text:
                        await self._process_transcript(transcript)

            except Exception as e:
                logger.error(f"Transcription error: {e}")
                await asyncio.sleep(0.1)

    async def _process_transcript(self, transcript: Dict[str, Any]) -> None:
        """Process new transcript segment"""
        # Add to meeting state
        self.meeting_state.transcript.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": transcript.get("speaker", "unknown"),
            "text": transcript["text"],
            "confidence": transcript.get("confidence", 1.0)
        })

        # Trigger callback
        if self.on_transcript_update:
            await self.on_transcript_update(transcript)

        # Analyze for response need
        should_respond = await self._should_respond(transcript["text"])
        if should_respond:
            await self._queue_response(transcript["text"])

    async def _should_respond(self, text: str) -> bool:
        """Determine if avatar should respond to current statement"""
        if self.mode == ParticipationMode.PASSIVE:
            return False

        # Check for direct mentions
        if self.personality_system.profile.name.lower() in text.lower():
            return True

        # Check for questions
        if "?" in text:
            relevance = await self.decision_engine.assess_relevance(
                text,
                self.meeting_state.topics_discussed
            )
            return relevance > 0.7

        # Check for decision points
        decision_keywords = ["should we", "what do you think", "any objections", "agree", "vote"]
        if any(keyword in text.lower() for keyword in decision_keywords):
            return self.mode == ParticipationMode.ACTIVE

        return False

    async def _queue_response(self, trigger_text: str) -> None:
        """Queue a response for generation"""
        await self.response_queue.put({
            "trigger": trigger_text,
            "timestamp": datetime.now(),
            "context": self._get_recent_context()
        })

    async def _response_generation_loop(self) -> None:
        """Generate responses for queued triggers"""
        while self.is_processing:
            try:
                # Get next response trigger
                trigger = await asyncio.wait_for(
                    self.response_queue.get(),
                    timeout=1.0
                )

                # Generate response
                response = await self._generate_response(
                    trigger["trigger"],
                    trigger["context"]
                )

                if response and response.should_speak:
                    # Add slight delay for natural conversation flow
                    await asyncio.sleep(0.5 + np.random.random() * 1.5)

                    # Speak the response
                    await self.speak(response.text)

                    # Record contribution
                    self.meeting_state.my_contributions.append({
                        "timestamp": datetime.now().isoformat(),
                        "text": response.text,
                        "confidence": response.confidence,
                        "reasoning": response.reasoning
                    })

                    # Trigger callback
                    if self.on_response_generated:
                        await self.on_response_generated(response)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Response generation error: {e}")

    async def _generate_response(
        self,
        trigger: str,
        context: List[Dict]
    ) -> Optional[AvatarResponse]:
        """Generate an intelligent response based on context and personality"""
        try:
            # Build comprehensive prompt
            prompt = await self._build_response_prompt(trigger, context)

            # Use GPT-4 for response generation
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.personality_system.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.personality_system.profile.creativity_level,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Create structured response
            avatar_response = AvatarResponse(
                text=result.get("response", ""),
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", ""),
                should_speak=result.get("should_speak", True),
                priority=result.get("priority", 5),
                action_items=result.get("action_items", []),
                follow_ups=result.get("follow_ups", []),
                sentiment=result.get("sentiment", "neutral")
            )

            # Validate with personality system
            avatar_response = self.personality_system.adjust_response(avatar_response)

            return avatar_response

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return None

    async def _build_response_prompt(self, trigger: str, context: List[Dict]) -> str:
        """Build comprehensive prompt for response generation"""
        prompt = f"""
        Meeting Context:
        - Type: {self.current_meeting.meeting_type if self.current_meeting else 'general'}
        - Phase: {self.meeting_state.meeting_phase}
        - Participants: {', '.join(self.meeting_state.participants[:5])}
        - Topics Discussed: {', '.join(self.meeting_state.topics_discussed[-3:])}

        Recent Conversation:
        {self._format_context(context)}

        Trigger Statement: "{trigger}"

        Your Profile:
        - Name: {self.personality_system.profile.name}
        - Role: {self.personality_system.profile.role}
        - Communication Style: {self.personality_system.profile.communication_style}
        - Expertise: {', '.join(self.personality_system.profile.expertise_areas[:3])}

        Previous Decisions Made:
        {self._format_decisions()}

        Generate a response that:
        1. Is appropriate for the meeting context
        2. Reflects your personality and expertise
        3. Adds value to the discussion
        4. Is concise and professional

        Return as JSON with fields:
        - response: Your actual response text
        - confidence: How confident you are (0-1)
        - reasoning: Brief explanation of your response
        - should_speak: Whether you should actually speak
        - priority: Response priority (1-10)
        - action_items: Any action items from your response
        - follow_ups: Any follow-up questions
        - sentiment: overall sentiment (positive/neutral/negative)
        """
        return prompt

    async def speak(self, text: str) -> None:
        """Convert text to speech and transmit"""
        try:
            # Generate audio
            audio_data = await self.voice_synthesizer.synthesize(
                text,
                voice_profile=self.personality_system.profile.voice_profile
            )

            # Transmit audio (would integrate with WebRTC here)
            logger.info(f"Avatar speaking: {text}")

            # In demo mode, also return text
            if self.mode == ParticipationMode.DEMO:
                print(f"\n🎯 AI Avatar: {text}\n")

        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")

    async def _generate_introduction(self) -> Optional[str]:
        """Generate meeting introduction"""
        if not self.current_meeting:
            return None

        intro_prompt = f"""
        Generate a brief, natural introduction for joining this meeting:
        - Meeting: {self.current_meeting.title}
        - Your name: {self.personality_system.profile.name}
        - Your role: {self.personality_system.profile.role}

        Keep it under 2 sentences, friendly but professional.
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are joining a meeting. Be concise and professional."},
                {"role": "user", "content": intro_prompt}
            ],
            max_tokens=100
        )

        return response.choices[0].message.content

    async def _analytics_loop(self) -> None:
        """Continuous meeting analytics"""
        while self.is_processing:
            try:
                await asyncio.sleep(30)  # Analyze every 30 seconds

                if len(self.meeting_state.transcript) > 5:
                    # Analyze meeting progress
                    analysis = await self.meeting_analyzer.analyze_meeting(
                        self.meeting_state.transcript,
                        self.meeting_state.decisions_made
                    )

                    # Update meeting state
                    if analysis:
                        self.meeting_state.topics_discussed = analysis.get("topics", [])
                        self.meeting_state.meeting_phase = analysis.get("phase", "discussion")

                        # Extract action items
                        new_actions = analysis.get("action_items", [])
                        for action in new_actions:
                            if action not in self.meeting_state.action_items:
                                self.meeting_state.action_items.append(action)
                                if self.on_action_item:
                                    await self.on_action_item(action)

            except Exception as e:
                logger.error(f"Analytics error: {e}")

    def _get_recent_context(self, num_messages: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        return self.meeting_state.transcript[-num_messages:]

    def _format_context(self, context: List[Dict]) -> str:
        """Format context for prompt"""
        formatted = []
        for msg in context[-5:]:  # Last 5 messages
            speaker = msg.get("speaker", "Unknown")
            text = msg.get("text", "")
            formatted.append(f"{speaker}: {text}")
        return "\n".join(formatted)

    def _format_decisions(self) -> str:
        """Format decisions for context"""
        if not self.meeting_state.decisions_made:
            return "No decisions made yet"

        formatted = []
        for decision in self.meeting_state.decisions_made[-3:]:
            formatted.append(f"- {decision.get('decision', '')}")
        return "\n".join(formatted)

    async def leave_meeting(self) -> Dict[str, Any]:
        """Leave meeting and generate summary"""
        self.is_processing = False

        # Generate meeting summary
        summary = await self.meeting_analyzer.generate_summary(
            self.meeting_state.transcript,
            self.meeting_state.decisions_made,
            self.meeting_state.action_items,
            self.meeting_state.my_contributions
        )

        return {
            "summary": summary,
            "duration": (datetime.now() - self.meeting_state.start_time).total_seconds(),
            "contributions": len(self.meeting_state.my_contributions),
            "action_items": self.meeting_state.action_items,
            "decisions": self.meeting_state.decisions_made
        }

    async def handle_direct_question(self, question: str) -> AvatarResponse:
        """Handle a direct question to the avatar"""
        context = self._get_recent_context()
        response = await self._generate_response(question, context)

        if response:
            await self.speak(response.text)

        return response

    def get_meeting_stats(self) -> Dict[str, Any]:
        """Get current meeting statistics"""
        return {
            "duration": (datetime.now() - self.meeting_state.start_time).total_seconds(),
            "total_statements": len(self.meeting_state.transcript),
            "my_contributions": len(self.meeting_state.my_contributions),
            "action_items": len(self.meeting_state.action_items),
            "decisions": len(self.meeting_state.decisions_made),
            "participants": len(self.meeting_state.participants),
            "current_phase": self.meeting_state.meeting_phase,
            "topics": self.meeting_state.topics_discussed
        }