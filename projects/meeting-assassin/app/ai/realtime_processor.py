"""
Real-time Meeting Processing and Event Handling System
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
from asyncio import Queue, Task
import aioredis
from app.ai.llm_analyzer import LLMAnalyzer, MeetingInsight, AnalysisDepth
from app.ai.enhanced_personality import EnhancedPersonalityEngine, PersonalityType
from app.ai.calendar_intelligence import CalendarIntelligence
import hashlib

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of real-time events"""
    MEETING_CREATED = "meeting_created"
    MEETING_UPDATED = "meeting_updated"
    MEETING_CANCELLED = "meeting_cancelled"
    CALENDAR_SYNC = "calendar_sync"
    USER_FEEDBACK = "user_feedback"
    OPTIMIZATION_TRIGGERED = "optimization_triggered"
    AI_DECISION_MADE = "ai_decision_made"
    PATTERN_DETECTED = "pattern_detected"


class ProcessingPriority(Enum):
    """Processing priority levels"""
    CRITICAL = 1  # Immediate processing
    HIGH = 2      # Process within 1 minute
    MEDIUM = 3    # Process within 5 minutes
    LOW = 4       # Process within 15 minutes


@dataclass
class ProcessingEvent:
    """Event for processing queue"""
    event_type: EventType
    priority: ProcessingPriority
    data: Dict[str, Any]
    user_id: str
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'event_type': self.event_type.value,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ProcessingResult:
    """Result of event processing"""
    event_type: EventType
    success: bool
    result: Dict[str, Any]
    processing_time_ms: float
    timestamp: datetime
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat()
        }


class RealtimeProcessor:
    """Real-time event processor for meeting intelligence"""

    def __init__(
        self,
        llm_analyzer: Optional[LLMAnalyzer] = None,
        redis_url: Optional[str] = None
    ):
        self.llm_analyzer = llm_analyzer or LLMAnalyzer()
        self.personality_engine = EnhancedPersonalityEngine(self.llm_analyzer)
        self.calendar_intelligence = CalendarIntelligence()

        # Processing queues by priority
        self.queues = {
            ProcessingPriority.CRITICAL: Queue(maxsize=100),
            ProcessingPriority.HIGH: Queue(maxsize=500),
            ProcessingPriority.MEDIUM: Queue(maxsize=1000),
            ProcessingPriority.LOW: Queue(maxsize=2000)
        }

        # Event handlers
        self.event_handlers: Dict[EventType, Callable] = {
            EventType.MEETING_CREATED: self._handle_meeting_created,
            EventType.MEETING_UPDATED: self._handle_meeting_updated,
            EventType.MEETING_CANCELLED: self._handle_meeting_cancelled,
            EventType.CALENDAR_SYNC: self._handle_calendar_sync,
            EventType.USER_FEEDBACK: self._handle_user_feedback,
            EventType.OPTIMIZATION_TRIGGERED: self._handle_optimization,
            EventType.AI_DECISION_MADE: self._handle_ai_decision,
            EventType.PATTERN_DETECTED: self._handle_pattern_detected
        }

        # Processing tasks
        self.processing_tasks: List[Task] = []
        self.is_running = False

        # Results cache
        self.results_cache: Dict[str, ProcessingResult] = {}
        self.cache_ttl = 3600  # 1 hour

        # Redis for distributed processing (optional)
        self.redis_client = None
        self.redis_url = redis_url

        # Websocket connections for real-time updates
        self.websocket_connections: Dict[str, Any] = {}

        # Metrics
        self.metrics = {
            "events_processed": 0,
            "events_failed": 0,
            "average_processing_time": 0,
            "queue_sizes": {}
        }

    async def start(self):
        """Start the real-time processor"""
        if self.is_running:
            return

        logger.info("Starting real-time processor")
        self.is_running = True

        # Initialize Redis if configured
        if self.redis_url:
            try:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
                logger.info("Connected to Redis for distributed processing")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")

        # Start processing tasks for each priority
        for priority in ProcessingPriority:
            task = asyncio.create_task(self._process_queue(priority))
            self.processing_tasks.append(task)

        # Start metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics())
        self.processing_tasks.append(metrics_task)

        logger.info("Real-time processor started successfully")

    async def stop(self):
        """Stop the real-time processor"""
        if not self.is_running:
            return

        logger.info("Stopping real-time processor")
        self.is_running = False

        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        # Close Redis connection
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

        logger.info("Real-time processor stopped")

    async def process_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        user_id: str,
        priority: Optional[ProcessingPriority] = None
    ) -> str:
        """
        Add an event to the processing queue
        Returns event ID for tracking
        """

        # Determine priority if not specified
        if priority is None:
            priority = self._determine_priority(event_type, data)

        # Create event
        event = ProcessingEvent(
            event_type=event_type,
            priority=priority,
            data=data,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )

        # Generate event ID
        event_id = self._generate_event_id(event)

        # Add to appropriate queue
        queue = self.queues[priority]

        try:
            await asyncio.wait_for(
                queue.put((event_id, event)),
                timeout=1.0
            )
            logger.info(f"Event {event_id} added to {priority.name} queue")

            # Notify via websocket if connected
            await self._notify_websocket(user_id, {
                "type": "event_queued",
                "event_id": event_id,
                "event_type": event_type.value,
                "priority": priority.value
            })

            return event_id

        except asyncio.TimeoutError:
            logger.error(f"Queue full for priority {priority.name}")
            raise Exception(f"Processing queue full, please retry later")

    async def _process_queue(self, priority: ProcessingPriority):
        """Process events from a specific priority queue"""

        queue = self.queues[priority]
        delay_map = {
            ProcessingPriority.CRITICAL: 0,
            ProcessingPriority.HIGH: 1,
            ProcessingPriority.MEDIUM: 5,
            ProcessingPriority.LOW: 15
        }
        delay = delay_map[priority]

        while self.is_running:
            try:
                # Wait for event with timeout
                event_data = await asyncio.wait_for(
                    queue.get(),
                    timeout=30.0
                )

                event_id, event = event_data

                # Add processing delay based on priority
                if delay > 0:
                    await asyncio.sleep(delay)

                # Process the event
                start_time = datetime.utcnow()
                result = await self._process_single_event(event)
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Create processing result
                processing_result = ProcessingResult(
                    event_type=event.event_type,
                    success=result.get("success", False),
                    result=result,
                    processing_time_ms=processing_time,
                    timestamp=datetime.utcnow(),
                    error_message=result.get("error")
                )

                # Cache result
                self.results_cache[event_id] = processing_result

                # Update metrics
                self.metrics["events_processed"] += 1
                self._update_average_processing_time(processing_time)

                # Notify via websocket
                await self._notify_websocket(event.user_id, {
                    "type": "event_processed",
                    "event_id": event_id,
                    "result": processing_result.to_dict()
                })

                logger.info(f"Processed event {event_id} in {processing_time:.2f}ms")

            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.metrics["events_failed"] += 1

    async def _process_single_event(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Process a single event"""

        try:
            handler = self.event_handlers.get(event.event_type)
            if not handler:
                return {"success": False, "error": f"No handler for {event.event_type.value}"}

            # Execute handler
            result = await handler(event)

            return {"success": True, **result}

        except Exception as e:
            logger.error(f"Error handling event {event.event_type.value}: {e}")

            # Retry logic
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                # Re-queue with lower priority
                new_priority = ProcessingPriority(min(4, event.priority.value + 1))
                await self.process_event(
                    event.event_type,
                    event.data,
                    event.user_id,
                    new_priority
                )
                return {"success": False, "error": str(e), "retrying": True}

            return {"success": False, "error": str(e)}

    async def _handle_meeting_created(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle new meeting creation"""

        meeting_data = event.data["meeting"]
        user_id = event.user_id

        # Analyze the meeting
        insight = await self.llm_analyzer.analyze_meeting(
            meeting_data,
            AnalysisDepth.STANDARD
        )

        # Get AI decision from personality engine
        user_personality = event.data.get("personality", PersonalityType.PROFESSIONAL)
        decision = await self.personality_engine.make_personality_decision(
            user_personality,
            meeting_data,
            insight
        )

        # Check for calendar patterns
        user_meetings = event.data.get("user_meetings", [])
        if user_meetings:
            patterns = await self.calendar_intelligence.analyze_calendar_patterns(
                user_meetings
            )
        else:
            patterns = {}

        # Generate response
        response = {
            "meeting_id": meeting_data.get("id"),
            "insight": insight.to_dict(),
            "decision": decision.to_dict(),
            "patterns": patterns,
            "actions": self._generate_immediate_actions(insight, decision)
        }

        # Store in cache if Redis available
        if self.redis_client:
            cache_key = f"meeting_analysis:{meeting_data.get('id')}"
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(response)
            )

        return response

    async def _handle_meeting_updated(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle meeting update"""

        meeting_data = event.data["meeting"]
        changes = event.data.get("changes", {})

        # Quick re-analysis if significant changes
        significant_changes = any(
            field in changes for field in ["start_time", "duration", "attendees", "title"]
        )

        if significant_changes:
            # Full re-analysis
            insight = await self.llm_analyzer.analyze_meeting(
                meeting_data,
                AnalysisDepth.QUICK
            )

            return {
                "meeting_id": meeting_data.get("id"),
                "updated_insight": insight.to_dict(),
                "significant_changes": True,
                "recommendations": self._generate_update_recommendations(changes, insight)
            }
        else:
            return {
                "meeting_id": meeting_data.get("id"),
                "significant_changes": False,
                "action": "No re-analysis needed"
            }

    async def _handle_meeting_cancelled(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle meeting cancellation"""

        meeting_id = event.data["meeting_id"]
        cancellation_time = event.data.get("cancellation_time")

        # Calculate time reclaimed
        original_duration = event.data.get("duration_minutes", 30)

        # Generate suggestions for reclaimed time
        suggestions = [
            "Use for focused deep work",
            "Schedule a break for mental reset",
            "Catch up on pending tasks",
            "Review and respond to important emails"
        ]

        return {
            "meeting_id": meeting_id,
            "time_reclaimed": original_duration,
            "suggestions": suggestions,
            "cancellation_time": cancellation_time
        }

    async def _handle_calendar_sync(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle full calendar sync"""

        meetings = event.data.get("meetings", [])
        user_id = event.user_id

        # Comprehensive calendar analysis
        analysis = await self.calendar_intelligence.analyze_calendar_patterns(
            meetings,
            event.data.get("user_context"),
            depth="deep"
        )

        # Generate optimization plan
        optimization_plan = self._generate_optimization_plan(analysis)

        return {
            "user_id": user_id,
            "total_meetings": len(meetings),
            "analysis": analysis,
            "optimization_plan": optimization_plan,
            "sync_timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_user_feedback(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle user feedback on AI decisions"""

        decision_id = event.data["decision_id"]
        feedback = event.data["feedback"]
        personality = event.data.get("personality")

        # Update personality engine with feedback
        await self.personality_engine.learn_from_feedback(
            decision_id,
            feedback,
            personality
        )

        return {
            "decision_id": decision_id,
            "feedback_processed": True,
            "learning_applied": True
        }

    async def _handle_optimization(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle optimization trigger"""

        optimization_type = event.data.get("type", "general")
        meetings = event.data.get("meetings", [])

        if optimization_type == "reschedule":
            # Find optimal reschedule times
            suggestions = await self.calendar_intelligence.suggest_optimal_times(
                event.data.get("duration_minutes", 30),
                meetings,
                event.data.get("constraints")
            )

            return {
                "optimization_type": "reschedule",
                "suggestions": suggestions
            }

        elif optimization_type == "batch":
            # Batch similar meetings
            batching_plan = self._create_batching_plan(meetings)

            return {
                "optimization_type": "batch",
                "batching_plan": batching_plan
            }

        else:
            # General optimization
            analysis = await self.calendar_intelligence.analyze_calendar_patterns(meetings)

            return {
                "optimization_type": "general",
                "analysis": analysis,
                "recommendations": analysis.get("optimizations", [])
            }

    async def _handle_ai_decision(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle AI decision event"""

        decision = event.data["decision"]
        meeting_id = event.data["meeting_id"]

        # Log decision for learning
        logger.info(f"AI Decision for meeting {meeting_id}: {decision}")

        # Generate execution plan
        execution_plan = self._generate_execution_plan(decision)

        return {
            "meeting_id": meeting_id,
            "decision": decision,
            "execution_plan": execution_plan,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_pattern_detected(self, event: ProcessingEvent) -> Dict[str, Any]:
        """Handle detected pattern"""

        pattern = event.data["pattern"]
        affected_meetings = event.data.get("affected_meetings", [])

        # Generate action items for pattern
        actions = self._generate_pattern_actions(pattern)

        return {
            "pattern": pattern,
            "affected_meetings": affected_meetings,
            "recommended_actions": actions,
            "priority": self._determine_pattern_priority(pattern)
        }

    def _determine_priority(
        self,
        event_type: EventType,
        data: Dict[str, Any]
    ) -> ProcessingPriority:
        """Determine processing priority for an event"""

        # Critical priority for urgent meetings
        if event_type == EventType.MEETING_CREATED:
            meeting = data.get("meeting", {})
            if "urgent" in meeting.get("title", "").lower():
                return ProcessingPriority.CRITICAL
            if meeting.get("start_time"):
                start_time = datetime.fromisoformat(meeting["start_time"])
                if (start_time - datetime.utcnow()).total_seconds() < 3600:  # Within 1 hour
                    return ProcessingPriority.CRITICAL

        # High priority for user feedback
        if event_type == EventType.USER_FEEDBACK:
            return ProcessingPriority.HIGH

        # Medium priority for updates
        if event_type in [EventType.MEETING_UPDATED, EventType.PATTERN_DETECTED]:
            return ProcessingPriority.MEDIUM

        # Default to low priority
        return ProcessingPriority.LOW

    def _generate_event_id(self, event: ProcessingEvent) -> str:
        """Generate unique event ID"""
        data = f"{event.user_id}:{event.event_type.value}:{event.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _generate_immediate_actions(
        self,
        insight: MeetingInsight,
        decision: Any
    ) -> List[Dict[str, Any]]:
        """Generate immediate action items"""

        actions = []

        if decision.decision == "decline":
            actions.append({
                "action": "send_decline",
                "priority": "high",
                "template": decision.response_template
            })

        elif decision.decision == "accept":
            if insight.required_preparation:
                actions.append({
                    "action": "schedule_prep_time",
                    "priority": "medium",
                    "duration": 15,
                    "items": insight.required_preparation[:3]
                })

        elif decision.decision == "reschedule":
            actions.append({
                "action": "propose_alternatives",
                "priority": "high",
                "alternatives": decision.alternative_options
            })

        return actions

    def _generate_update_recommendations(
        self,
        changes: Dict[str, Any],
        insight: MeetingInsight
    ) -> List[str]:
        """Generate recommendations based on meeting updates"""

        recommendations = []

        if "duration" in changes:
            if changes["duration"] > 60:
                recommendations.append("Consider breaking into multiple shorter sessions")

        if "attendees" in changes:
            new_count = len(changes.get("attendees", []))
            if new_count > 8:
                recommendations.append("Large group - consider if all attendees are essential")

        if "start_time" in changes:
            recommendations.append("Notify all attendees of time change immediately")

        return recommendations

    def _generate_optimization_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive optimization plan"""

        plan = {
            "immediate_actions": [],
            "weekly_goals": [],
            "monthly_targets": []
        }

        # Based on analysis, create actionable plan
        if analysis.get("productivity_insight", {}).get("focus_time_ratio", 0) < 0.3:
            plan["immediate_actions"].append("Block 2-hour focus time tomorrow morning")
            plan["weekly_goals"].append("Achieve 40% focus time ratio")

        optimizations = analysis.get("optimizations", [])
        for opt in optimizations[:3]:  # Top 3 optimizations
            plan["immediate_actions"].append(opt.get("title", ""))

        return plan

    def _create_batching_plan(self, meetings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create plan for batching similar meetings"""

        # Group meetings by similarity
        groups = {}
        for meeting in meetings:
            # Simple grouping by title keywords
            title = meeting.get("title", "").lower()
            if "status" in title or "update" in title:
                key = "status_updates"
            elif "1:1" in title or "one-on-one" in title:
                key = "one_on_ones"
            elif "review" in title:
                key = "reviews"
            else:
                key = "other"

            if key not in groups:
                groups[key] = []
            groups[key].append(meeting)

        # Create batching recommendations
        plan = {"batches": []}
        for group_name, group_meetings in groups.items():
            if len(group_meetings) > 1:
                plan["batches"].append({
                    "type": group_name,
                    "meetings": [m.get("id") for m in group_meetings],
                    "recommendation": f"Batch {len(group_meetings)} {group_name} together",
                    "time_saved": len(group_meetings) * 10  # 10 min per meeting from batching
                })

        return plan

    def _generate_execution_plan(self, decision: str) -> List[Dict[str, Any]]:
        """Generate plan for executing AI decision"""

        plans = {
            "accept": [
                {"step": 1, "action": "Send acceptance"},
                {"step": 2, "action": "Block calendar time"},
                {"step": 3, "action": "Add preparation reminder"}
            ],
            "decline": [
                {"step": 1, "action": "Send polite decline"},
                {"step": 2, "action": "Offer alternative (if applicable)"},
                {"step": 3, "action": "Request meeting notes"}
            ],
            "reschedule": [
                {"step": 1, "action": "Propose new times"},
                {"step": 2, "action": "Explain conflict"},
                {"step": 3, "action": "Await confirmation"}
            ],
            "delegate": [
                {"step": 1, "action": "Identify delegate"},
                {"step": 2, "action": "Brief delegate"},
                {"step": 3, "action": "Inform organizer"}
            ]
        }

        return plans.get(decision, [{"step": 1, "action": "Manual review required"}])

    def _generate_pattern_actions(self, pattern: Dict[str, Any]) -> List[str]:
        """Generate actions for detected pattern"""

        pattern_type = pattern.get("pattern_type", "")
        actions = []

        if pattern_type == "meeting_cluster":
            actions.extend([
                "Add 15-minute buffers between meetings",
                "Decline non-essential meetings in cluster",
                "Schedule break after cluster"
            ])
        elif pattern_type == "focus_time_block":
            actions.extend([
                "Block this time in calendar",
                "Set auto-decline for this period",
                "Communicate focus hours to team"
            ])
        elif pattern_type == "meeting_fatigue_zone":
            actions.extend([
                "Redistribute meetings across the day",
                "Implement meeting-free hours",
                "Convert some meetings to async"
            ])

        return actions

    def _determine_pattern_priority(self, pattern: Dict[str, Any]) -> str:
        """Determine priority of detected pattern"""

        impact_score = pattern.get("impact_score", 0)
        optimization_potential = pattern.get("optimization_potential", 0)

        combined_score = (abs(impact_score) + optimization_potential) / 2

        if combined_score > 0.7:
            return "high"
        elif combined_score > 0.4:
            return "medium"
        else:
            return "low"

    async def _notify_websocket(self, user_id: str, data: Dict[str, Any]):
        """Send notification via websocket if connected"""

        if user_id in self.websocket_connections:
            try:
                ws = self.websocket_connections[user_id]
                await ws.send_json(data)
            except Exception as e:
                logger.error(f"Failed to send websocket notification: {e}")
                # Remove broken connection
                del self.websocket_connections[user_id]

    def _update_average_processing_time(self, new_time: float):
        """Update average processing time metric"""

        current_avg = self.metrics["average_processing_time"]
        count = self.metrics["events_processed"]

        # Calculate new average
        self.metrics["average_processing_time"] = (
            (current_avg * (count - 1) + new_time) / count
        )

    async def _collect_metrics(self):
        """Collect and update metrics"""

        while self.is_running:
            try:
                # Update queue sizes
                for priority, queue in self.queues.items():
                    self.metrics["queue_sizes"][priority.name] = queue.qsize()

                # Log metrics periodically
                if self.metrics["events_processed"] % 100 == 0:
                    logger.info(f"Metrics: {self.metrics}")

                # Sleep for 30 seconds
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")

    async def get_processing_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a processing event"""

        if event_id in self.results_cache:
            return self.results_cache[event_id].to_dict()

        # Check Redis if available
        if self.redis_client:
            cache_key = f"processing_result:{event_id}"
            result = await self.redis_client.get(cache_key)
            if result:
                return json.loads(result)

        return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

    def register_websocket(self, user_id: str, websocket: Any):
        """Register websocket connection for user"""
        self.websocket_connections[user_id] = websocket
        logger.info(f"Websocket registered for user {user_id}")

    def unregister_websocket(self, user_id: str):
        """Unregister websocket connection"""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]
            logger.info(f"Websocket unregistered for user {user_id}")