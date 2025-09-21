"""
AI Intelligence API Endpoints
Comprehensive AI-powered meeting analysis and decision making
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.models.database import get_db
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.core.config import settings

# Import our AI modules
from app.ai.llm_analyzer import LLMAnalyzer, AnalysisDepth, MeetingInsight
from app.ai.enhanced_personality import EnhancedPersonalityEngine, PersonalityType, PersonalityDecision
from app.ai.calendar_intelligence import CalendarIntelligence
from app.ai.realtime_processor import RealtimeProcessor, EventType, ProcessingPriority

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize AI components
llm_analyzer = LLMAnalyzer(api_key=settings.OPENAI_API_KEY)
personality_engine = EnhancedPersonalityEngine(llm_analyzer)
calendar_intelligence = CalendarIntelligence()
realtime_processor = RealtimeProcessor(llm_analyzer, settings.REDIS_URL)


@router.on_event("startup")
async def startup_event():
    """Initialize real-time processor on startup"""
    await realtime_processor.start()
    logger.info("AI Intelligence system initialized")


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await realtime_processor.stop()
    logger.info("AI Intelligence system shutdown")


@router.post("/analyze-meeting")
async def analyze_meeting(
    meeting_data: Dict[str, Any],
    depth: str = "standard",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Comprehensive AI analysis of a meeting

    Args:
        meeting_data: Meeting information
        depth: Analysis depth (quick/standard/deep/executive)

    Returns:
        Detailed AI analysis with insights and recommendations
    """
    try:
        # Convert depth string to enum
        analysis_depth = AnalysisDepth[depth.upper()]

        # Get user context if user_id provided
        user_context = None
        if "user_id" in meeting_data:
            # Fetch user's recent meetings for context
            user_context = await _get_user_context(meeting_data["user_id"], db)

        # Perform AI analysis
        insight = await llm_analyzer.analyze_meeting(
            meeting_data,
            analysis_depth,
            user_context
        )

        # Generate natural language summary
        summary = await llm_analyzer.generate_natural_explanation(
            "analyze",
            meeting_data.get("title", "Meeting"),
            insight.to_dict(),
            user_context
        )

        return {
            "success": True,
            "insight": insight.to_dict(),
            "summary": summary,
            "analysis_depth": depth,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Meeting analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/personality-decision")
async def get_personality_decision(
    meeting_data: Dict[str, Any],
    personality: str = "professional",
    compare_all: bool = False,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get AI decision based on personality type

    Args:
        meeting_data: Meeting information
        personality: Personality type (professional/assertive/collaborative/protective/efficient)
        compare_all: Whether to compare decisions from all personalities

    Returns:
        AI decision with personality-based reasoning
    """
    try:
        # Parse personality type
        personality_type = PersonalityType[personality.upper()]

        # Get user context
        user_context = None
        if "user_id" in meeting_data:
            user_context = await _get_user_context(meeting_data["user_id"], db)

        if compare_all:
            # Get ensemble decision from all personalities
            result = await personality_engine.get_ensemble_decision(
                meeting_data,
                user_context,
                primary_personality=personality_type
            )
        else:
            # Analyze meeting first
            insight = await llm_analyzer.analyze_meeting(
                meeting_data,
                AnalysisDepth.STANDARD,
                user_context
            )

            # Get decision from specific personality
            decision = await personality_engine.make_personality_decision(
                personality_type,
                meeting_data,
                insight,
                user_context
            )

            result = {
                "decision": decision.to_dict(),
                "insight": insight.to_dict(),
                "personality": personality
            }

        return {
            "success": True,
            **result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Personality decision failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-calendar-patterns")
async def analyze_calendar_patterns(
    user_id: str,
    days_back: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze calendar patterns for optimization opportunities

    Args:
        user_id: User ID
        days_back: Number of days to analyze

    Returns:
        Calendar patterns, productivity insights, and optimization recommendations
    """
    try:
        # Fetch user's meetings
        meetings = await _get_user_meetings(user_id, days_back, db)

        # Get user preferences
        user_context = await _get_user_context(user_id, db)

        # Perform pattern analysis
        analysis = await calendar_intelligence.analyze_calendar_patterns(
            meetings,
            user_context,
            depth="deep"
        )

        # Use LLM to generate additional insights if available
        if llm_analyzer.client:
            llm_patterns = await llm_analyzer.analyze_calendar_patterns(
                meetings[-20:],  # Recent 20 meetings
                meetings[:20],   # Upcoming 20 meetings
                user_context.get("preferences")
            )
            analysis["llm_insights"] = llm_patterns

        return {
            "success": True,
            "analysis": analysis,
            "meeting_count": len(meetings),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Calendar pattern analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-optimal-times")
async def suggest_optimal_meeting_times(
    duration_minutes: int,
    user_id: str,
    constraints: Optional[Dict[str, Any]] = None,
    num_suggestions: int = 3,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Suggest optimal meeting times based on calendar analysis

    Args:
        duration_minutes: Meeting duration
        user_id: User ID
        constraints: Optional constraints for scheduling
        num_suggestions: Number of suggestions to return

    Returns:
        Optimal time slot suggestions with quality scores
    """
    try:
        # Get user's existing meetings
        meetings = await _get_user_meetings(user_id, 14, db)  # Next 14 days

        # Get suggestions
        suggestions = await calendar_intelligence.suggest_optimal_times(
            duration_minutes,
            meetings,
            constraints,
            num_suggestions
        )

        return {
            "success": True,
            "suggestions": suggestions,
            "duration_minutes": duration_minutes,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Time suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-event")
async def process_calendar_event(
    event_type: str,
    event_data: Dict[str, Any],
    user_id: str,
    priority: Optional[str] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Process a calendar event in real-time

    Args:
        event_type: Type of event (meeting_created, meeting_updated, etc.)
        event_data: Event data
        user_id: User ID
        priority: Processing priority (critical/high/medium/low)

    Returns:
        Event processing ID for tracking
    """
    try:
        # Parse event type and priority
        event_type_enum = EventType[event_type.upper()]
        priority_enum = ProcessingPriority[priority.upper()] if priority else None

        # Queue event for processing
        event_id = await realtime_processor.process_event(
            event_type_enum,
            event_data,
            user_id,
            priority_enum
        )

        return {
            "success": True,
            "event_id": event_id,
            "status": "queued",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Event processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-status/{event_id}")
async def get_event_status(event_id: str) -> Dict[str, Any]:
    """
    Get status of a processing event

    Args:
        event_id: Event ID from process_event

    Returns:
        Current status and results if available
    """
    try:
        status = await realtime_processor.get_processing_status(event_id)

        if status:
            return {
                "success": True,
                "status": "completed",
                "result": status
            }
        else:
            return {
                "success": True,
                "status": "processing",
                "result": None
            }

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze")
async def batch_analyze_meetings(
    meeting_ids: List[str],
    analysis_type: str = "quick",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Batch analyze multiple meetings

    Args:
        meeting_ids: List of meeting IDs
        analysis_type: Type of analysis (quick/standard/deep)

    Returns:
        Analysis results for all meetings
    """
    try:
        results = []
        depth = AnalysisDepth[analysis_type.upper()]

        for meeting_id in meeting_ids:
            # Fetch meeting data
            meeting = await _get_meeting_by_id(meeting_id, db)
            if meeting:
                # Analyze meeting
                insight = await llm_analyzer.analyze_meeting(
                    meeting,
                    depth
                )
                results.append({
                    "meeting_id": meeting_id,
                    "title": meeting.get("title"),
                    "insight": insight.to_dict()
                })

        return {
            "success": True,
            "analyzed_count": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-meeting-brief")
async def generate_meeting_brief(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate comprehensive meeting brief with AI insights

    Args:
        meeting_id: Meeting ID

    Returns:
        Complete meeting brief with preparation points and expected outcomes
    """
    try:
        # Get meeting data
        meeting = await _get_meeting_by_id(meeting_id, db)

        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")

        # Analyze meeting
        insight = await llm_analyzer.analyze_meeting(
            meeting,
            AnalysisDepth.DEEP
        )

        # Generate brief
        brief = {
            "meeting_title": meeting.get("title"),
            "start_time": meeting.get("start_time"),
            "duration": meeting.get("duration_minutes"),
            "importance_score": insight.importance_score,
            "key_topics": insight.key_topics,
            "required_preparation": insight.required_preparation,
            "expected_outcomes": insight.expected_outcomes,
            "decision_points": insight.decision_points,
            "attendee_analysis": insight.attendee_analysis,
            "potential_blockers": insight.potential_blockers,
            "suggested_questions": [
                "What are the success criteria for this meeting?",
                "What decisions need to be made today?",
                "What are the next steps after this meeting?"
            ],
            "efficiency_tips": insight.efficiency_recommendations,
            "ai_summary": insight.generated_summary
        }

        return {
            "success": True,
            "brief": brief,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Brief generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-schedule")
async def optimize_user_schedule(
    user_id: str,
    optimization_type: str = "general",
    constraints: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Optimize user's schedule with AI recommendations

    Args:
        user_id: User ID
        optimization_type: Type of optimization (general/reschedule/batch)
        constraints: Optional optimization constraints

    Returns:
        Optimization plan with specific recommendations
    """
    try:
        # Get user's meetings
        meetings = await _get_user_meetings(user_id, 30, db)

        # Trigger optimization event
        event_id = await realtime_processor.process_event(
            EventType.OPTIMIZATION_TRIGGERED,
            {
                "type": optimization_type,
                "meetings": meetings,
                "constraints": constraints
            },
            user_id,
            ProcessingPriority.HIGH
        )

        # Wait for processing (with timeout)
        import asyncio
        for _ in range(10):  # Wait up to 10 seconds
            status = await realtime_processor.get_processing_status(event_id)
            if status:
                return {
                    "success": True,
                    "optimization": status.get("result"),
                    "event_id": event_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            await asyncio.sleep(1)

        return {
            "success": True,
            "status": "processing",
            "event_id": event_id,
            "message": "Optimization in progress, check status endpoint"
        }

    except Exception as e:
        logger.error(f"Schedule optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personality-stats/{personality}")
async def get_personality_statistics(personality: str) -> Dict[str, Any]:
    """
    Get statistics for a specific AI personality

    Args:
        personality: Personality type

    Returns:
        Decision statistics and performance metrics
    """
    try:
        personality_type = PersonalityType[personality.upper()]
        stats = personality_engine.get_personality_stats(personality_type)

        return {
            "success": True,
            "personality": personality,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get AI system performance metrics

    Returns:
        System metrics including processing stats and queue sizes
    """
    try:
        metrics = realtime_processor.get_metrics()

        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/ai-updates/{user_id}")
async def ai_updates_websocket(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time AI updates

    Args:
        websocket: WebSocket connection
        user_id: User ID
    """
    await websocket.accept()

    # Register websocket with processor
    realtime_processor.register_websocket(user_id, websocket)

    try:
        while True:
            # Keep connection alive and handle messages
            data = await websocket.receive_text()

            # Process commands
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                # Echo for now
                await websocket.send_json({
                    "type": "echo",
                    "message": data
                })

    except WebSocketDisconnect:
        realtime_processor.unregister_websocket(user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")


# Helper functions

async def _get_user_context(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get user context for AI analysis"""
    # This would fetch from database
    # For now, return mock context
    return {
        "user_id": user_id,
        "preferences": {
            "preferred_meeting_hours": [10, 11, 14, 15],
            "avoid_days": [],
            "focus_time_preference": "morning"
        },
        "stress_level": 0.5,
        "calendar_density": 0.6,
        "focus_time_ratio": 0.3
    }


async def _get_user_meetings(user_id: str, days: int, db: AsyncSession) -> List[Dict[str, Any]]:
    """Get user's meetings for specified days"""
    # This would fetch from database
    # For now, return mock data
    return [
        {
            "id": f"meeting_{i}",
            "title": f"Meeting {i}",
            "start_time": (datetime.now() + timedelta(days=i, hours=10)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=i, hours=11)).isoformat(),
            "duration_minutes": 60,
            "attendees": ["user@example.com", "colleague@example.com"],
            "importance_score": 0.7
        }
        for i in range(min(days, 10))
    ]


async def _get_meeting_by_id(meeting_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
    """Get meeting by ID"""
    # This would fetch from database
    # For now, return mock data
    return {
        "id": meeting_id,
        "title": "Important Strategy Meeting",
        "description": "Quarterly planning session",
        "start_time": (datetime.now() + timedelta(days=1, hours=14)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=15, minutes=30)).isoformat(),
        "duration_minutes": 90,
        "attendees": ["ceo@company.com", "cto@company.com", "user@company.com"],
        "organizer_email": "ceo@company.com",
        "location": "Conference Room A"
    }