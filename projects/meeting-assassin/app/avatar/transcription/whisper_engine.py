"""
OpenAI Whisper Integration for Real-time Transcription
"""

import asyncio
import io
import wave
import struct
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import os
import logging
from openai import AsyncOpenAI
import webrtcvad
import soundfile as sf
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio"""
    text: str
    start_time: float
    end_time: float
    confidence: float = 1.0
    speaker: Optional[str] = None
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioBuffer:
    """Buffer for audio data processing"""
    data: bytes = b""
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2  # 16-bit audio
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())


class WhisperTranscriptionEngine:
    """
    Real-time transcription engine using OpenAI Whisper
    """

    def __init__(
        self,
        api_key: str,
        model: str = "whisper-1",
        language: str = "en",
        sample_rate: int = 16000,
        buffer_duration: float = 2.0  # seconds
    ):
        """Initialize Whisper transcription engine"""
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.language = language
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration

        # Audio processing
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        self.audio_buffer = deque(maxlen=int(sample_rate * buffer_duration))
        self.current_segment = AudioBuffer(sample_rate=sample_rate)

        # Transcription state
        self.is_active = False
        self.transcript_history: List[TranscriptionSegment] = []
        self.processing_queue = asyncio.Queue()
        self.last_transcript_time = 0

        # Speaker diarization (simple implementation)
        self.speakers: Dict[str, Any] = {}
        self.current_speaker = "Speaker 1"

    async def start(self) -> None:
        """Start the transcription engine"""
        self.is_active = True
        asyncio.create_task(self._process_audio_queue())
        logger.info("Whisper transcription engine started")

    async def stop(self) -> None:
        """Stop the transcription engine"""
        self.is_active = False
        # Process any remaining audio
        if len(self.audio_buffer) > 0:
            await self._process_buffer()
        logger.info("Whisper transcription engine stopped")

    async def add_audio(self, audio_data: bytes) -> None:
        """Add audio data to processing queue"""
        if not self.is_active:
            return

        # Add to buffer
        self.audio_buffer.extend(audio_data)

        # Check if we should process
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_transcript_time >= self.buffer_duration:
            await self._process_buffer()
            self.last_transcript_time = current_time

    async def transcribe_stream(self, audio_data: bytes) -> Optional[TranscriptionSegment]:
        """Transcribe audio stream in real-time"""
        try:
            # Convert bytes to proper audio format
            audio_array = self._bytes_to_array(audio_data)

            # Apply voice activity detection
            if not self._has_voice_activity(audio_array):
                return None

            # Create temporary file for Whisper API
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                self._write_wav(tmp_file.name, audio_array)

                # Transcribe using Whisper API
                with open(tmp_file.name, "rb") as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        language=self.language,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )

                # Clean up
                os.unlink(tmp_file.name)

            # Process response
            if transcript and transcript.text:
                segment = TranscriptionSegment(
                    text=transcript.text.strip(),
                    start_time=asyncio.get_event_loop().time() - self.buffer_duration,
                    end_time=asyncio.get_event_loop().time(),
                    language=transcript.language or self.language,
                    confidence=1.0
                )

                # Simple speaker tracking
                segment.speaker = await self._identify_speaker(audio_array)

                # Add to history
                self.transcript_history.append(segment)

                return segment

            return None

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def _process_audio_queue(self) -> None:
        """Process audio from queue continuously"""
        while self.is_active:
            try:
                # Process queued audio
                if not self.processing_queue.empty():
                    audio_data = await self.processing_queue.get()
                    segment = await self.transcribe_stream(audio_data)
                    if segment:
                        logger.debug(f"Transcribed: {segment.text}")
                else:
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Audio processing error: {e}")

    async def _process_buffer(self) -> None:
        """Process accumulated audio buffer"""
        if len(self.audio_buffer) == 0:
            return

        # Convert buffer to bytes
        audio_data = bytes(self.audio_buffer)
        self.audio_buffer.clear()

        # Add to processing queue
        await self.processing_queue.put(audio_data)

    def _bytes_to_array(self, audio_bytes: bytes) -> np.ndarray:
        """Convert bytes to numpy array"""
        return np.frombuffer(audio_bytes, dtype=np.int16)

    def _array_to_bytes(self, audio_array: np.ndarray) -> bytes:
        """Convert numpy array to bytes"""
        return audio_array.astype(np.int16).tobytes()

    def _has_voice_activity(self, audio_array: np.ndarray) -> bool:
        """Check if audio contains voice activity"""
        try:
            # Convert to bytes for VAD
            audio_bytes = self._array_to_bytes(audio_array)

            # Check frames for voice activity
            frame_duration = 30  # ms
            frame_size = int(self.sample_rate * frame_duration / 1000) * 2  # bytes

            num_voiced_frames = 0
            total_frames = 0

            for i in range(0, len(audio_bytes) - frame_size, frame_size):
                frame = audio_bytes[i:i + frame_size]
                if len(frame) == frame_size:
                    is_speech = self.vad.is_speech(frame, self.sample_rate)
                    if is_speech:
                        num_voiced_frames += 1
                    total_frames += 1

            # Return true if more than 30% of frames contain speech
            if total_frames > 0:
                voice_ratio = num_voiced_frames / total_frames
                return voice_ratio > 0.3

            return False

        except Exception as e:
            logger.error(f"VAD error: {e}")
            return True  # Default to processing if VAD fails

    def _write_wav(self, filename: str, audio_array: np.ndarray) -> None:
        """Write audio array to WAV file"""
        sf.write(filename, audio_array, self.sample_rate)

    async def _identify_speaker(self, audio_array: np.ndarray) -> str:
        """Simple speaker identification based on audio characteristics"""
        # This is a placeholder - in production, you'd use speaker diarization models
        # For now, use simple energy-based detection
        energy = np.sqrt(np.mean(audio_array ** 2))

        # Simple threshold-based speaker detection
        if energy > 1000:
            return "Speaker 1"
        elif energy > 500:
            return "Speaker 2"
        else:
            return "Speaker 3"

    def get_full_transcript(self) -> str:
        """Get full transcript as text"""
        return "\n".join([
            f"[{segment.speaker or 'Unknown'}]: {segment.text}"
            for segment in self.transcript_history
        ])

    def get_recent_transcript(self, duration: float = 30.0) -> List[TranscriptionSegment]:
        """Get recent transcript segments"""
        current_time = asyncio.get_event_loop().time()
        cutoff_time = current_time - duration

        return [
            segment for segment in self.transcript_history
            if segment.end_time >= cutoff_time
        ]

    async def transcribe_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Transcribe an audio file"""
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=self.language,
                    response_format="verbose_json"
                )

            if transcript:
                return {
                    "text": transcript.text,
                    "language": transcript.language,
                    "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                    "segments": transcript.segments if hasattr(transcript, 'segments') else []
                }

            return None

        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return None

    def clear_history(self) -> None:
        """Clear transcript history"""
        self.transcript_history.clear()
        self.audio_buffer.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get transcription statistics"""
        total_segments = len(self.transcript_history)
        total_duration = sum(
            segment.end_time - segment.start_time
            for segment in self.transcript_history
        ) if total_segments > 0 else 0

        speakers = {}
        for segment in self.transcript_history:
            speaker = segment.speaker or "Unknown"
            if speaker not in speakers:
                speakers[speaker] = 0
            speakers[speaker] += 1

        return {
            "total_segments": total_segments,
            "total_duration": total_duration,
            "speakers": speakers,
            "average_confidence": np.mean([s.confidence for s in self.transcript_history])
                                if total_segments > 0 else 0,
            "words_transcribed": sum(len(s.text.split()) for s in self.transcript_history)
        }


class EnhancedTranscriptionEngine(WhisperTranscriptionEngine):
    """Enhanced transcription with additional features"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keywords_detected: List[Tuple[str, float]] = []
        self.emotion_history: List[Dict[str, Any]] = []

    async def process_with_analysis(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Process audio with additional analysis"""
        # Get base transcription
        segment = await self.transcribe_stream(audio_data)

        if not segment:
            return None

        # Perform additional analysis
        result = {
            "segment": segment,
            "keywords": await self._extract_keywords(segment.text),
            "emotion": await self._detect_emotion(audio_data),
            "intent": await self._classify_intent(segment.text)
        }

        return result

    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - would use NLP models in production
        important_words = ["decision", "action", "deadline", "budget", "priority", "blocker"]
        found_keywords = [word for word in important_words if word.lower() in text.lower()]
        return found_keywords

    async def _detect_emotion(self, audio_data: bytes) -> str:
        """Detect emotion from audio"""
        # Placeholder - would use emotion detection models
        return "neutral"

    async def _classify_intent(self, text: str) -> str:
        """Classify speaker intent"""
        # Simple intent classification
        if "?" in text:
            return "question"
        elif any(word in text.lower() for word in ["should", "must", "need to"]):
            return "directive"
        elif any(word in text.lower() for word in ["agree", "yes", "correct"]):
            return "agreement"
        elif any(word in text.lower() for word in ["no", "disagree", "but"]):
            return "disagreement"
        else:
            return "statement"