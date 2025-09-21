"""
AI Meeting Avatar System - Core Module
Autonomous meeting participation with personality-driven responses
"""

from .core.avatar_engine import AvatarEngine
from .core.personality_system import PersonalitySystem
from .core.meeting_context import MeetingContext
from .transcription.whisper_engine import WhisperTranscriptionEngine
from .synthesis.voice_synthesizer import VoiceSynthesizer
from .intelligence.meeting_analyzer import MeetingAnalyzer

__all__ = [
    "AvatarEngine",
    "PersonalitySystem",
    "MeetingContext",
    "WhisperTranscriptionEngine",
    "VoiceSynthesizer",
    "MeetingAnalyzer"
]