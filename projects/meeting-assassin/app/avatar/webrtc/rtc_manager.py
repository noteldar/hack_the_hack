"""
WebRTC Manager - Handle real-time audio/video communication
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder, MediaBlackhole
from av import AudioFrame, VideoFrame
import av
import fractions

logger = logging.getLogger(__name__)


@dataclass
class RTCConfig:
    """WebRTC configuration"""
    ice_servers: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]}
    ])
    audio_codec: str = "opus"
    video_codec: str = "VP8"
    audio_bitrate: int = 128000
    video_bitrate: int = 1000000
    enable_video: bool = False  # Audio-only by default for meetings
    echo_cancellation: bool = True
    noise_suppression: bool = True
    auto_gain_control: bool = True


class AudioTrack(MediaStreamTrack):
    """Custom audio track for processing and synthesis"""
    kind = "audio"

    def __init__(self, synthesizer=None):
        super().__init__()
        self.synthesizer = synthesizer
        self.sample_rate = 48000
        self.channels = 2
        self.samples_per_frame = 960  # 20ms at 48kHz
        self._timestamp = 0
        self._audio_buffer = asyncio.Queue()

    async def recv(self):
        """Receive audio frame"""
        pts = self._timestamp
        self._timestamp += self.samples_per_frame
        time_base = fractions.Fraction(1, self.sample_rate)

        # Get audio from buffer or generate silence
        try:
            audio_data = await asyncio.wait_for(
                self._audio_buffer.get(),
                timeout=0.02  # 20ms timeout
            )
        except asyncio.TimeoutError:
            # Generate silence
            audio_data = np.zeros((self.samples_per_frame, self.channels), dtype=np.int16)

        # Create audio frame
        frame = AudioFrame.from_ndarray(audio_data, format='s16', layout='stereo')
        frame.pts = pts
        frame.time_base = time_base
        frame.sample_rate = self.sample_rate

        return frame

    async def add_audio(self, audio_data: bytes):
        """Add audio data to buffer"""
        await self._audio_buffer.put(audio_data)


class VideoTrack(MediaStreamTrack):
    """Custom video track for avatar display"""
    kind = "video"

    def __init__(self, avatar_renderer=None):
        super().__init__()
        self.avatar_renderer = avatar_renderer
        self.width = 640
        self.height = 480
        self.fps = 30
        self._timestamp = 0

    async def recv(self):
        """Receive video frame"""
        pts = self._timestamp
        self._timestamp += 1
        time_base = fractions.Fraction(1, self.fps)

        # Generate avatar video frame
        if self.avatar_renderer:
            frame_data = await self.avatar_renderer.render_frame()
        else:
            # Generate placeholder frame
            frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            # Add some visual indicator
            frame_data[100:150, 100:150] = [0, 255, 0]  # Green square

        # Create video frame
        frame = VideoFrame.from_ndarray(frame_data, format='rgb24')
        frame.pts = pts
        frame.time_base = time_base

        return frame


class WebRTCManager:
    """
    Manages WebRTC connections for meeting participation
    """

    def __init__(
        self,
        config: Optional[RTCConfig] = None,
        on_audio_received: Optional[Callable] = None,
        on_video_received: Optional[Callable] = None
    ):
        """Initialize WebRTC manager"""
        self.config = config or RTCConfig()
        self.peer_connections: Dict[str, RTCPeerConnection] = {}

        # Callbacks
        self.on_audio_received = on_audio_received
        self.on_video_received = on_video_received

        # Media tracks
        self.audio_track: Optional[AudioTrack] = None
        self.video_track: Optional[VideoTrack] = None

        # Recording
        self.recorder: Optional[MediaRecorder] = None
        self.is_recording = False

    async def create_peer_connection(self, peer_id: str) -> RTCPeerConnection:
        """Create a new peer connection"""
        try:
            # Create RTC configuration
            rtc_config = {
                "iceServers": self.config.ice_servers
            }

            # Create peer connection
            pc = RTCPeerConnection(configuration=rtc_config)

            # Add to connections
            self.peer_connections[peer_id] = pc

            # Set up event handlers
            @pc.on("track")
            async def on_track(track):
                await self._handle_track(peer_id, track)

            @pc.on("datachannel")
            def on_datachannel(channel):
                self._handle_datachannel(peer_id, channel)

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                logger.info(f"Connection state for {peer_id}: {pc.connectionState}")
                if pc.connectionState == "connected":
                    await self._on_connected(peer_id)
                elif pc.connectionState == "failed":
                    await self._on_failed(peer_id)

            logger.info(f"Created peer connection for {peer_id}")
            return pc

        except Exception as e:
            logger.error(f"Failed to create peer connection: {e}")
            raise

    async def create_offer(self, peer_id: str) -> Dict[str, Any]:
        """Create WebRTC offer"""
        try:
            pc = self.peer_connections.get(peer_id)
            if not pc:
                pc = await self.create_peer_connection(peer_id)

            # Add tracks
            await self._add_tracks(pc)

            # Create offer
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)

            return {
                "type": offer.type,
                "sdp": offer.sdp
            }

        except Exception as e:
            logger.error(f"Failed to create offer: {e}")
            raise

    async def handle_offer(
        self,
        peer_id: str,
        offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle WebRTC offer and create answer"""
        try:
            pc = self.peer_connections.get(peer_id)
            if not pc:
                pc = await self.create_peer_connection(peer_id)

            # Set remote description
            await pc.setRemoteDescription(RTCSessionDescription(
                sdp=offer["sdp"],
                type=offer["type"]
            ))

            # Add tracks
            await self._add_tracks(pc)

            # Create answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            return {
                "type": answer.type,
                "sdp": answer.sdp
            }

        except Exception as e:
            logger.error(f"Failed to handle offer: {e}")
            raise

    async def handle_answer(self, peer_id: str, answer: Dict[str, Any]) -> None:
        """Handle WebRTC answer"""
        try:
            pc = self.peer_connections.get(peer_id)
            if not pc:
                raise ValueError(f"No peer connection for {peer_id}")

            await pc.setRemoteDescription(RTCSessionDescription(
                sdp=answer["sdp"],
                type=answer["type"]
            ))

            logger.info(f"Set remote description for {peer_id}")

        except Exception as e:
            logger.error(f"Failed to handle answer: {e}")
            raise

    async def add_ice_candidate(
        self,
        peer_id: str,
        candidate: Dict[str, Any]
    ) -> None:
        """Add ICE candidate"""
        try:
            pc = self.peer_connections.get(peer_id)
            if not pc:
                raise ValueError(f"No peer connection for {peer_id}")

            await pc.addIceCandidate(candidate)
            logger.debug(f"Added ICE candidate for {peer_id}")

        except Exception as e:
            logger.error(f"Failed to add ICE candidate: {e}")

    async def _add_tracks(self, pc: RTCPeerConnection) -> None:
        """Add media tracks to peer connection"""
        # Add audio track
        if not self.audio_track:
            self.audio_track = AudioTrack()
        pc.addTrack(self.audio_track)

        # Add video track if enabled
        if self.config.enable_video:
            if not self.video_track:
                self.video_track = VideoTrack()
            pc.addTrack(self.video_track)

    async def _handle_track(self, peer_id: str, track: MediaStreamTrack) -> None:
        """Handle incoming media track"""
        logger.info(f"Received {track.kind} track from {peer_id}")

        if track.kind == "audio":
            asyncio.create_task(self._process_audio_track(peer_id, track))
        elif track.kind == "video":
            asyncio.create_task(self._process_video_track(peer_id, track))

    async def _process_audio_track(self, peer_id: str, track: MediaStreamTrack) -> None:
        """Process incoming audio track"""
        try:
            while True:
                frame = await track.recv()

                # Convert to numpy array
                audio_data = frame.to_ndarray()

                # Process audio
                if self.on_audio_received:
                    await self.on_audio_received(peer_id, audio_data)

                # Record if enabled
                if self.is_recording and self.recorder:
                    await self.recorder.write(frame)

        except Exception as e:
            logger.error(f"Audio processing error: {e}")

    async def _process_video_track(self, peer_id: str, track: MediaStreamTrack) -> None:
        """Process incoming video track"""
        try:
            while True:
                frame = await track.recv()

                # Convert to numpy array
                video_data = frame.to_ndarray()

                # Process video
                if self.on_video_received:
                    await self.on_video_received(peer_id, video_data)

        except Exception as e:
            logger.error(f"Video processing error: {e}")

    def _handle_datachannel(self, peer_id: str, channel) -> None:
        """Handle data channel"""
        logger.info(f"Data channel opened with {peer_id}")

        @channel.on("message")
        def on_message(message):
            self._handle_datachannel_message(peer_id, message)

    def _handle_datachannel_message(self, peer_id: str, message: str) -> None:
        """Handle data channel message"""
        try:
            data = json.loads(message)
            logger.debug(f"Data channel message from {peer_id}: {data}")
            # Handle control messages, metadata, etc.
        except Exception as e:
            logger.error(f"Failed to handle data channel message: {e}")

    async def _on_connected(self, peer_id: str) -> None:
        """Handle successful connection"""
        logger.info(f"Successfully connected to {peer_id}")

    async def _on_failed(self, peer_id: str) -> None:
        """Handle failed connection"""
        logger.error(f"Connection failed for {peer_id}")
        await self.close_connection(peer_id)

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio to all peers"""
        if self.audio_track:
            await self.audio_track.add_audio(audio_data)

    async def start_recording(self, filename: str) -> None:
        """Start recording session"""
        try:
            self.recorder = MediaRecorder(filename)
            self.is_recording = True
            logger.info(f"Started recording to {filename}")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")

    async def stop_recording(self) -> None:
        """Stop recording session"""
        if self.recorder and self.is_recording:
            self.is_recording = False
            await self.recorder.stop()
            self.recorder = None
            logger.info("Stopped recording")

    async def close_connection(self, peer_id: str) -> None:
        """Close peer connection"""
        pc = self.peer_connections.get(peer_id)
        if pc:
            await pc.close()
            del self.peer_connections[peer_id]
            logger.info(f"Closed connection for {peer_id}")

    async def close_all_connections(self) -> None:
        """Close all peer connections"""
        for peer_id in list(self.peer_connections.keys()):
            await self.close_connection(peer_id)

    def get_connection_stats(self, peer_id: str) -> Dict[str, Any]:
        """Get connection statistics"""
        pc = self.peer_connections.get(peer_id)
        if not pc:
            return {}

        return {
            "connection_state": pc.connectionState,
            "ice_connection_state": pc.iceConnectionState,
            "ice_gathering_state": pc.iceGatheringState,
            "signaling_state": pc.signalingState
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all connections"""
        return {
            peer_id: self.get_connection_stats(peer_id)
            for peer_id in self.peer_connections
        }