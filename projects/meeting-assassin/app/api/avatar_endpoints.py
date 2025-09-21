"""
API Endpoints for AI Avatar System
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks, status
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio
import logging
from pydantic import BaseModel, Field

from ..avatar.core.avatar_engine import AvatarEngine, ParticipationMode
from ..avatar.core.personality_system import (
    PersonalityProfile, PersonalityPresets,
    CommunicationStyle, DecisionStyle
)
from ..avatar.core.meeting_context import MeetingContext, MeetingType, MeetingPriority
from ..avatar.webrtc.rtc_manager import WebRTCManager, RTCConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/avatar", tags=["AI Avatar"])


# Pydantic models for API
class PersonalityConfig(BaseModel):
    """Personality configuration request"""
    name: str = Field(..., description="Avatar name")
    role: str = Field(..., description="Avatar role")
    communication_style: str = Field(default="diplomatic")
    assertiveness: float = Field(default=0.6, ge=0, le=1)
    empathy_level: float = Field(default=0.7, ge=0, le=1)
    participation_frequency: float = Field(default=0.6, ge=0, le=1)
    expertise_areas: List[str] = Field(default_factory=list)
    preset: Optional[str] = Field(None, description="Use preset personality")


class MeetingJoinRequest(BaseModel):
    """Request to join a meeting"""
    meeting_id: str
    meeting_title: str
    meeting_type: str = "general"
    platform: str = "zoom"
    meeting_url: Optional[str] = None
    participation_mode: str = "active"
    auto_respond: bool = True


class ResponseRequest(BaseModel):
    """Manual response request"""
    text: str
    context: Optional[Dict[str, Any]] = None


class TrainingDataRequest(BaseModel):
    """Training data for avatar"""
    category: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


# Global avatar instances (would use proper state management in production)
active_avatars: Dict[str, AvatarEngine] = {}
avatar_connections: Dict[str, WebSocket] = {}


@router.post("/create")
async def create_avatar(config: PersonalityConfig) -> Dict[str, Any]:
    """Create a new AI avatar with personality configuration"""
    try:
        # Create personality profile
        if config.preset:
            # Use preset
            presets = {
                "executive": PersonalityPresets.get_executive(),
                "engineer": PersonalityPresets.get_engineer(),
                "product_manager": PersonalityPresets.get_product_manager(),
                "sales": PersonalityPresets.get_sales()
            }
            profile = presets.get(config.preset)
            if not profile:
                raise HTTPException(status_code=400, detail="Invalid preset")
        else:
            # Create custom profile
            profile = PersonalityProfile(
                name=config.name,
                role=config.role,
                communication_style=CommunicationStyle(config.communication_style),
                assertiveness=config.assertiveness,
                empathy_level=config.empathy_level,
                participation_frequency=config.participation_frequency,
                expertise_areas=config.expertise_areas
            )

        # Create avatar engine
        avatar = AvatarEngine(
            personality_profile=profile,
            openai_api_key="your-openai-key",  # Would get from env
            mode=ParticipationMode.ACTIVE
        )

        # Store avatar
        avatar_id = f"avatar_{datetime.now().timestamp()}"
        active_avatars[avatar_id] = avatar

        return {
            "avatar_id": avatar_id,
            "profile": profile.name,
            "role": profile.role,
            "status": "created",
            "capabilities": {
                "transcription": True,
                "voice_synthesis": True,
                "meeting_analysis": True,
                "autonomous_responses": True
            }
        }

    except Exception as e:
        logger.error(f"Failed to create avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{avatar_id}/join-meeting")
async def join_meeting(
    avatar_id: str,
    request: MeetingJoinRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Have avatar join a meeting"""
    avatar = active_avatars.get(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    try:
        # Create meeting context
        meeting_context = MeetingContext(
            meeting_id=request.meeting_id,
            title=request.meeting_title,
            meeting_type=MeetingType(request.meeting_type),
            platform=request.platform,
            meeting_url=request.meeting_url,
            ai_participation_level=request.participation_mode,
            auto_respond=request.auto_respond
        )

        # Set participation mode
        avatar.mode = ParticipationMode(request.participation_mode)

        # Join meeting in background
        background_tasks.add_task(avatar.join_meeting, meeting_context)

        return {
            "status": "joining",
            "meeting_id": request.meeting_id,
            "avatar_id": avatar_id,
            "participation_mode": request.participation_mode
        }

    except Exception as e:
        logger.error(f"Failed to join meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{avatar_id}/leave-meeting")
async def leave_meeting(avatar_id: str) -> Dict[str, Any]:
    """Have avatar leave current meeting"""
    avatar = active_avatars.get(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    try:
        summary = await avatar.leave_meeting()
        return {
            "status": "left",
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Failed to leave meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{avatar_id}/respond")
async def manual_response(
    avatar_id: str,
    request: ResponseRequest
) -> Dict[str, Any]:
    """Trigger manual response from avatar"""
    avatar = active_avatars.get(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    try:
        response = await avatar.handle_direct_question(request.text)

        return {
            "response": response.text,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "action_items": response.action_items
        }

    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{avatar_id}/stats")
async def get_avatar_stats(avatar_id: str) -> Dict[str, Any]:
    """Get current avatar statistics"""
    avatar = active_avatars.get(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    return avatar.get_meeting_stats()


@router.post("/{avatar_id}/train")
async def train_avatar(
    avatar_id: str,
    data: TrainingDataRequest
) -> Dict[str, Any]:
    """Add training data to avatar's knowledge base"""
    avatar = active_avatars.get(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    try:
        # Add to knowledge base
        entry_id = await avatar.knowledge_base.add_knowledge(
            content=data.content,
            source="training",
            category=data.category,
            metadata=data.metadata
        )

        return {
            "status": "trained",
            "entry_id": entry_id,
            "category": data.category
        }

    except Exception as e:
        logger.error(f"Failed to train avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/{avatar_id}/stream")
async def avatar_stream(websocket: WebSocket, avatar_id: str):
    """WebSocket endpoint for real-time avatar updates"""
    await websocket.accept()

    avatar = active_avatars.get(avatar_id)
    if not avatar:
        await websocket.send_json({"error": "Avatar not found"})
        await websocket.close()
        return

    # Store connection
    avatar_connections[avatar_id] = websocket

    try:
        # Set up callbacks
        async def on_transcript(transcript):
            await websocket.send_json({
                "type": "transcript",
                "data": transcript
            })

        async def on_response(response):
            await websocket.send_json({
                "type": "response",
                "data": {
                    "text": response.text,
                    "confidence": response.confidence,
                    "reasoning": response.reasoning
                }
            })

        async def on_action(action):
            await websocket.send_json({
                "type": "action_item",
                "data": action
            })

        # Register callbacks
        avatar.on_transcript_update = on_transcript
        avatar.on_response_generated = on_response
        avatar.on_action_item = on_action

        # Keep connection alive
        while True:
            try:
                # Wait for messages
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message["type"] == "audio":
                    # Process audio data
                    audio_data = base64.b64decode(message["data"])
                    await avatar.process_audio_stream(audio_data)

                elif message["type"] == "command":
                    # Handle commands
                    await handle_command(avatar, message["command"])

                elif message["type"] == "ping":
                    # Send pong
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({"error": str(e)})

    finally:
        # Clean up
        if avatar_id in avatar_connections:
            del avatar_connections[avatar_id]

        # Clear callbacks
        avatar.on_transcript_update = None
        avatar.on_response_generated = None
        avatar.on_action_item = None


@router.get("/personalities")
async def get_personality_presets() -> Dict[str, Any]:
    """Get available personality presets"""
    return {
        "presets": [
            {
                "id": "executive",
                "name": "Executive",
                "description": "Assertive, decision-focused executive personality"
            },
            {
                "id": "engineer",
                "name": "Software Engineer",
                "description": "Technical, analytical engineering personality"
            },
            {
                "id": "product_manager",
                "name": "Product Manager",
                "description": "Diplomatic, user-focused product personality"
            },
            {
                "id": "sales",
                "name": "Sales",
                "description": "Empathetic, relationship-focused sales personality"
            }
        ]
    }


@router.post("/demo/simulate-meeting")
async def simulate_meeting() -> Dict[str, Any]:
    """Simulate a demo meeting for hackathon"""
    try:
        # Create demo avatar
        profile = PersonalityPresets.get_product_manager()
        avatar = AvatarEngine(
            personality_profile=profile,
            openai_api_key="demo-key",
            mode=ParticipationMode.DEMO
        )

        # Create demo meeting context
        meeting_context = MeetingContext(
            meeting_id="demo_001",
            title="Product Planning Meeting",
            meeting_type=MeetingType.PLANNING,
            priority=MeetingPriority.HIGH
        )

        # Simulate meeting
        await avatar.join_meeting(meeting_context)

        # Simulate some interactions
        demo_transcript = [
            {"speaker": "John", "text": "Let's discuss the new feature roadmap."},
            {"speaker": "Sarah", "text": "I think we should prioritize mobile experience."},
            {"speaker": "John", "text": f"{profile.name}, what's your perspective on this?"}
        ]

        responses = []
        for entry in demo_transcript:
            if profile.name in entry["text"]:
                response = await avatar.handle_direct_question(entry["text"])
                responses.append({
                    "trigger": entry["text"],
                    "response": response.text,
                    "confidence": response.confidence
                })

        # Get summary
        summary = await avatar.leave_meeting()

        return {
            "demo": "completed",
            "avatar": profile.name,
            "interactions": responses,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Demo simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_avatars() -> Dict[str, Any]:
    """Get list of active avatars"""
    return {
        "avatars": [
            {
                "id": avatar_id,
                "name": avatar.personality_system.profile.name,
                "role": avatar.personality_system.profile.role,
                "status": "active" if avatar.is_processing else "idle",
                "meeting": avatar.current_meeting.title if avatar.current_meeting else None
            }
            for avatar_id, avatar in active_avatars.items()
        ]
    }


async def handle_command(avatar: AvatarEngine, command: Dict[str, Any]) -> None:
    """Handle WebSocket commands"""
    cmd_type = command.get("type")

    if cmd_type == "set_mode":
        mode = command.get("mode")
        if mode:
            avatar.mode = ParticipationMode(mode)

    elif cmd_type == "update_personality":
        traits = command.get("traits", {})
        for key, value in traits.items():
            if hasattr(avatar.personality_system.profile, key):
                setattr(avatar.personality_system.profile, key, value)