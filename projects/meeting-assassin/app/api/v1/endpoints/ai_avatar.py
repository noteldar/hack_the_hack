"""
AI Avatar personality and decision-making endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional

from app.models.database import get_db
from app.models.user import User
from app.models.meeting import Meeting
from app.schemas.ai_avatar import (
    PersonalityUpdate, DecisionRequest, DecisionResponse,
    PersonalityAnalysis, AvatarStats
)
from app.services.auth import AuthService
from app.services.ai_avatar import AIAvatarService
from app.core.websocket import WebSocketManager

router = APIRouter()
auth_service = AuthService()
ai_service = AIAvatarService()
websocket_manager = WebSocketManager()


@router.get("/personality")
async def get_personality_profile(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get AI avatar personality profile"""
    try:
        personality = await ai_service.get_personality_profile(current_user)
        return personality

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get personality profile: {str(e)}"
        )


@router.put("/personality")
async def update_personality(
    personality_update: PersonalityUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update AI avatar personality settings"""
    try:
        # Update personality in user profile
        current_user.avatar_personality = personality_update.personality_type
        current_user.ai_decision_autonomy = personality_update.decision_autonomy
        current_user.auto_decline_conflicts = personality_update.auto_decline_conflicts
        current_user.auto_suggest_reschedule = personality_update.auto_suggest_reschedule

        await db.commit()

        # Generate updated personality profile
        updated_profile = await ai_service.generate_personality_profile(
            personality_update.personality_type,
            personality_update.decision_autonomy,
            personality_update.traits or {}
        )

        return {
            "message": "Personality updated successfully",
            "personality": updated_profile
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update personality: {str(e)}"
        )


@router.post("/decide")
async def make_decision(
    decision_request: DecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Make an AI decision for a meeting or scheduling scenario"""
    try:
        # Get meeting if specified
        meeting = None
        if decision_request.meeting_id:
            meeting = await db.get(Meeting, decision_request.meeting_id)
            if not meeting or meeting.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Meeting not found"
                )

        # Make AI decision
        decision = await ai_service.make_decision(
            current_user,
            decision_request.scenario,
            decision_request.context,
            meeting
        )

        # Update meeting with decision if applicable
        if meeting:
            meeting.ai_decision = decision.decision_type
            meeting.ai_decision_confidence = decision.confidence
            meeting.ai_decision_reasoning = decision.reasoning
            meeting.last_ai_analysis = decision.timestamp
            await db.commit()

            # Send WebSocket update
            await websocket_manager.send_ai_decision(
                str(current_user.id),
                {
                    "meeting_id": meeting.id,
                    "decision": decision.decision_type,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "avatar_personality": current_user.avatar_personality
                }
            )

        return decision

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to make decision: {str(e)}"
        )


@router.get("/decisions/history")
async def get_decision_history(
    limit: int = 50,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI decision history"""
    try:
        history = await ai_service.get_decision_history(current_user.id, limit, db)
        return {"decisions": history, "total": len(history)}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get decision history: {str(e)}"
        )


@router.get("/stats", response_model=AvatarStats)
async def get_avatar_stats(
    days: int = 30,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI avatar performance statistics"""
    try:
        stats = await ai_service.get_avatar_stats(current_user.id, days, db)
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get avatar stats: {str(e)}"
        )


@router.post("/analyze/meeting/{meeting_id}")
async def analyze_meeting(
    meeting_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger AI analysis for a specific meeting"""
    meeting = await db.get(Meeting, meeting_id)

    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # Queue analysis
    background_tasks.add_task(
        ai_service.analyze_meeting,
        meeting_id,
        current_user.id
    )

    return {"message": "Analysis queued", "meeting_id": meeting_id}


@router.post("/train")
async def train_personality(
    feedback_data: Dict[str, Any],
    current_user: User = Depends(auth_service.get_current_user)
):
    """Train AI personality based on user feedback"""
    try:
        training_result = await ai_service.train_from_feedback(
            current_user.id,
            feedback_data
        )

        return {
            "message": "Training data processed",
            "improvements": training_result.get("improvements", []),
            "accuracy_improvement": training_result.get("accuracy_improvement", 0)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process training data: {str(e)}"
        )


@router.get("/suggestions")
async def get_ai_suggestions(
    context: str = "general",
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI suggestions for productivity and scheduling"""
    try:
        suggestions = await ai_service.get_suggestions(
            current_user,
            context,
            db
        )

        return {"suggestions": suggestions, "context": context}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.post("/bulk-analyze")
async def bulk_analyze_meetings(
    background_tasks: BackgroundTasks,
    days_ahead: int = 7,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Bulk analyze upcoming meetings"""
    try:
        # Queue bulk analysis
        background_tasks.add_task(
            ai_service.bulk_analyze_meetings,
            current_user.id,
            days_ahead
        )

        return {
            "message": f"Bulk analysis queued for next {days_ahead} days",
            "user_id": current_user.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue bulk analysis: {str(e)}"
        )