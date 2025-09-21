"""
Voice Synthesis System - Text-to-Speech with ElevenLabs and fallback options
"""

import asyncio
import io
import base64
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import logging
import numpy as np
import edge_tts
import pyttsx3
from elevenlabs import AsyncElevenLabs, Voice, VoiceSettings, play
from elevenlabs.client import AsyncGenerateResponse
import soundfile as sf

logger = logging.getLogger(__name__)


@dataclass
class VoiceConfig:
    """Voice configuration for synthesis"""
    provider: str = "elevenlabs"  # elevenlabs, edge, pyttsx3
    voice_id: str = "default"
    stability: float = 0.5
    similarity_boost: float = 0.5
    style: float = 0.0
    use_speaker_boost: bool = True
    language: str = "en"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0


class VoiceSynthesizer:
    """
    Multi-provider voice synthesis system
    """

    def __init__(
        self,
        elevenlabs_api_key: Optional[str] = None,
        default_config: Optional[VoiceConfig] = None
    ):
        """Initialize voice synthesizer"""
        self.config = default_config or VoiceConfig()

        # Initialize providers
        self.elevenlabs_client = None
        if elevenlabs_api_key:
            try:
                self.elevenlabs_client = AsyncElevenLabs(api_key=elevenlabs_api_key)
                logger.info("ElevenLabs initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ElevenLabs: {e}")

        # Initialize fallback TTS
        self.pyttsx_engine = pyttsx3.init()
        self._configure_pyttsx()

        # Voice cache for performance
        self.voice_cache: Dict[str, bytes] = {}
        self.available_voices: Dict[str, List[str]] = {
            "elevenlabs": [],
            "edge": [],
            "pyttsx3": []
        }

        # Audio processing
        self.sample_rate = 22050
        self.audio_format = "mp3"

    async def initialize(self) -> None:
        """Initialize and fetch available voices"""
        await self._fetch_available_voices()

    async def _fetch_available_voices(self) -> None:
        """Fetch available voices from all providers"""
        # ElevenLabs voices
        if self.elevenlabs_client:
            try:
                voices = await self.elevenlabs_client.voices.get_all()
                self.available_voices["elevenlabs"] = [v.voice_id for v in voices.voices]
            except Exception as e:
                logger.error(f"Failed to fetch ElevenLabs voices: {e}")

        # Edge TTS voices
        try:
            voices = await edge_tts.list_voices()
            self.available_voices["edge"] = [v["ShortName"] for v in voices]
        except Exception as e:
            logger.error(f"Failed to fetch Edge TTS voices: {e}")

        # Pyttsx3 voices
        try:
            voices = self.pyttsx_engine.getProperty('voices')
            self.available_voices["pyttsx3"] = [v.id for v in voices] if voices else []
        except Exception as e:
            logger.error(f"Failed to fetch pyttsx3 voices: {e}")

    def _configure_pyttsx(self) -> None:
        """Configure pyttsx3 engine"""
        try:
            # Set properties
            self.pyttsx_engine.setProperty('rate', 175)  # Speed
            self.pyttsx_engine.setProperty('volume', 1.0)  # Volume

            # Try to set a better voice
            voices = self.pyttsx_engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Prefer female voice for variety
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.pyttsx_engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            logger.warning(f"Failed to configure pyttsx3: {e}")

    async def synthesize(
        self,
        text: str,
        voice_profile: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None
    ) -> bytes:
        """Synthesize speech from text"""
        # Check cache
        if cache_key and cache_key in self.voice_cache:
            return self.voice_cache[cache_key]

        # Prepare voice config
        config = self._merge_config(voice_profile)

        # Try primary provider
        audio_data = None

        if config.provider == "elevenlabs" and self.elevenlabs_client:
            audio_data = await self._synthesize_elevenlabs(text, config)

        if not audio_data and config.provider == "edge":
            audio_data = await self._synthesize_edge(text, config)

        if not audio_data:
            audio_data = self._synthesize_pyttsx(text, config)

        # Cache result
        if audio_data and cache_key:
            self.voice_cache[cache_key] = audio_data

        return audio_data

    async def _synthesize_elevenlabs(self, text: str, config: VoiceConfig) -> Optional[bytes]:
        """Synthesize using ElevenLabs"""
        try:
            # Get or create voice
            voice_id = config.voice_id
            if voice_id == "default":
                # Use a default ElevenLabs voice
                voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

            # Generate audio
            audio_stream = await self.elevenlabs_client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=config.stability,
                        similarity_boost=config.similarity_boost,
                        style=config.style,
                        use_speaker_boost=config.use_speaker_boost
                    )
                ),
                model="eleven_monolingual_v1"
            )

            # Collect audio chunks
            audio_chunks = []
            async for chunk in audio_stream:
                if chunk:
                    audio_chunks.append(chunk)

            return b''.join(audio_chunks)

        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            return None

    async def _synthesize_edge(self, text: str, config: VoiceConfig) -> Optional[bytes]:
        """Synthesize using Edge TTS"""
        try:
            # Select voice
            voice = config.voice_id
            if voice == "default":
                voice = "en-US-AriaNeural"  # Default Edge voice

            # Configure synthesis
            communicate = edge_tts.Communicate(text, voice)

            # Set rate and pitch
            if config.speed != 1.0:
                rate_change = int((config.speed - 1.0) * 100)
                communicate.rate = f"{rate_change:+d}%"

            if config.pitch != 1.0:
                pitch_change = int((config.pitch - 1.0) * 50)
                communicate.pitch = f"{pitch_change:+d}Hz"

            # Generate audio
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            return audio_data

        except Exception as e:
            logger.error(f"Edge TTS synthesis failed: {e}")
            return None

    def _synthesize_pyttsx(self, text: str, config: VoiceConfig) -> bytes:
        """Synthesize using pyttsx3 (offline)"""
        try:
            # Configure voice properties
            self.pyttsx_engine.setProperty('rate', int(175 * config.speed))
            self.pyttsx_engine.setProperty('volume', config.volume)

            # Save to bytes
            output = io.BytesIO()
            self.pyttsx_engine.save_to_file(text, output)
            self.pyttsx_engine.runAndWait()

            return output.getvalue()

        except Exception as e:
            logger.error(f"Pyttsx3 synthesis failed: {e}")
            # Return empty audio as last resort
            return self._generate_silence(1.0)

    def _merge_config(self, voice_profile: Optional[Dict[str, Any]]) -> VoiceConfig:
        """Merge voice profile with default config"""
        if not voice_profile:
            return self.config

        config = VoiceConfig(
            provider=voice_profile.get("provider", self.config.provider),
            voice_id=voice_profile.get("voice_id", self.config.voice_id),
            stability=voice_profile.get("stability", self.config.stability),
            similarity_boost=voice_profile.get("similarity_boost", self.config.similarity_boost),
            style=voice_profile.get("style", self.config.style),
            use_speaker_boost=voice_profile.get("use_speaker_boost", self.config.use_speaker_boost),
            language=voice_profile.get("language", self.config.language),
            speed=voice_profile.get("speed", self.config.speed),
            pitch=voice_profile.get("pitch", self.config.pitch),
            volume=voice_profile.get("volume", self.config.volume)
        )

        return config

    def _generate_silence(self, duration: float) -> bytes:
        """Generate silence audio"""
        num_samples = int(self.sample_rate * duration)
        silence = np.zeros(num_samples, dtype=np.float32)

        # Convert to bytes
        output = io.BytesIO()
        sf.write(output, silence, self.sample_rate, format='WAV')
        return output.getvalue()

    async def create_voice_profile(
        self,
        name: str,
        description: str,
        samples: List[bytes]
    ) -> Optional[str]:
        """Create a custom voice profile from samples"""
        if not self.elevenlabs_client:
            logger.error("ElevenLabs client not initialized")
            return None

        try:
            # Create voice from samples
            voice = await self.elevenlabs_client.voices.add(
                name=name,
                description=description,
                files=samples
            )

            return voice.voice_id

        except Exception as e:
            logger.error(f"Failed to create voice profile: {e}")
            return None

    def get_available_voices(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """Get available voices"""
        if provider:
            return {provider: self.available_voices.get(provider, [])}
        return self.available_voices

    def clear_cache(self) -> None:
        """Clear voice cache"""
        self.voice_cache.clear()

    async def stream_synthesis(
        self,
        text: str,
        config: Optional[VoiceConfig] = None,
        chunk_size: int = 1024
    ) -> AsyncGenerator[bytes, None]:
        """Stream synthesized audio in chunks"""
        # Synthesize full audio
        audio_data = await self.synthesize(text, config)

        # Stream in chunks
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i:i + chunk_size]
            await asyncio.sleep(0.01)  # Small delay for streaming


class PersonalityVoiceMapper:
    """Maps personality traits to voice characteristics"""

    @staticmethod
    def map_personality_to_voice(personality_profile: Dict[str, Any]) -> VoiceConfig:
        """Map personality profile to voice configuration"""
        config = VoiceConfig()

        # Map assertiveness to stability
        assertiveness = personality_profile.get("assertiveness", 0.5)
        config.stability = 0.3 + (assertiveness * 0.4)  # 0.3 to 0.7

        # Map empathy to similarity boost
        empathy = personality_profile.get("empathy_level", 0.5)
        config.similarity_boost = 0.4 + (empathy * 0.3)  # 0.4 to 0.7

        # Map formality to style
        formality = personality_profile.get("formality_level", 0.5)
        config.style = formality * 0.5  # 0.0 to 0.5

        # Map energy/enthusiasm to speed
        participation = personality_profile.get("participation_frequency", 0.5)
        config.speed = 0.9 + (participation * 0.2)  # 0.9 to 1.1

        # Select voice based on personality
        communication_style = personality_profile.get("communication_style", "neutral")
        if communication_style == "formal":
            config.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Professional voice
        elif communication_style == "casual":
            config.voice_id = "yoZ06aMxZJJ28mfd3POQ"  # Friendly voice
        elif communication_style == "empathetic":
            config.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Warm voice
        else:
            config.voice_id = "default"

        return config


class AudioProcessor:
    """Process and enhance synthesized audio"""

    @staticmethod
    async def apply_effects(
        audio_data: bytes,
        effects: Dict[str, Any]
    ) -> bytes:
        """Apply audio effects"""
        # Load audio
        audio, sr = sf.read(io.BytesIO(audio_data))

        # Apply effects
        if effects.get("normalize", False):
            audio = AudioProcessor._normalize(audio)

        if effects.get("compress", False):
            audio = AudioProcessor._compress(audio)

        if "eq" in effects:
            audio = AudioProcessor._apply_eq(audio, effects["eq"], sr)

        # Convert back to bytes
        output = io.BytesIO()
        sf.write(output, audio, sr, format='WAV')
        return output.getvalue()

    @staticmethod
    def _normalize(audio: np.ndarray) -> np.ndarray:
        """Normalize audio volume"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * 0.95
        return audio

    @staticmethod
    def _compress(audio: np.ndarray, threshold: float = 0.7, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        # Simple compression
        mask = np.abs(audio) > threshold
        audio[mask] = threshold + (audio[mask] - threshold) / ratio
        return audio

    @staticmethod
    def _apply_eq(audio: np.ndarray, eq_settings: Dict[str, float], sr: int) -> np.ndarray:
        """Apply equalization"""
        # Placeholder - would use scipy.signal for actual implementation
        return audio