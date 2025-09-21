"""
AI-powered meeting intelligence service for autonomous calendar management
"""

import asyncio
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.user import User
from app.models.meeting import Meeting, AIDecisionType, MeetingPriority
from app.services.google_calendar import google_calendar_client, autonomous_calendar_manager
from app.services.oauth_service import oauth_service
from app.ai.personality import ai_personality_service
import logging

logger = logging.getLogger(__name__)


class MeetingIntelligenceService:
    """AI-powered meeting intelligence and autonomous decision making"""

    def __init__(self):
        self.calendar_client = google_calendar_client
        self.autonomous_manager = autonomous_calendar_manager
        self.oauth_service = oauth_service

    async def analyze_meeting(
        self,
        meeting_data: Dict[str, Any],
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze meeting and provide AI recommendations"""

        # Extract meeting information
        title = meeting_data.get("summary", "")
        description = meeting_data.get("description", "")
        attendees = meeting_data.get("attendees", [])
        start_time = datetime.fromisoformat(
            meeting_data["start"]["dateTime"].replace("Z", "+00:00")
        )
        end_time = datetime.fromisoformat(
            meeting_data["end"]["dateTime"].replace("Z", "+00:00")
        )

        # Get user's existing meetings for context
        existing_meetings = await self._get_user_meetings_for_period(
            user, db, start_time.date(), start_time.date() + timedelta(days=7)
        )

        analysis = {
            "importance_score": await self._calculate_importance_score(
                title, description, attendees, user
            ),
            "conflict_score": await self._calculate_conflict_score(
                start_time, end_time, existing_meetings, user
            ),
            "productivity_impact": await self._calculate_productivity_impact(
                start_time, end_time, title, user
            ),
            "meeting_type": self._classify_meeting_type(title, description),
            "required_preparation": await self._estimate_preparation_time(
                title, description, attendees
            ),
            "alternatives": await self._suggest_alternatives(
                start_time, end_time, existing_meetings
            )
        }

        # Make AI decision
        decision = await self._make_ai_decision(analysis, user)
        analysis["ai_decision"] = decision

        return analysis

    async def _calculate_importance_score(
        self,
        title: str,
        description: str,
        attendees: List[Dict],
        user: User
    ) -> float:
        """Calculate meeting importance score (0.0 to 1.0)"""
        score = 0.5  # Base score

        # High importance keywords
        high_importance_keywords = [
            "board", "executive", "ceo", "cto", "director", "vp",
            "urgent", "critical", "emergency", "crisis",
            "deadline", "launch", "release", "milestone",
            "client", "customer", "stakeholder", "investor",
            "decision", "strategy", "planning", "review"
        ]

        # Medium importance keywords
        medium_importance_keywords = [
            "meeting", "sync", "standup", "retrospective",
            "demo", "presentation", "training", "workshop",
            "interview", "onboarding", "team", "project"
        ]

        # Low importance keywords
        low_importance_keywords = [
            "coffee", "chat", "social", "optional",
            "fyi", "info", "update", "touch base"
        ]

        content = f"{title} {description}".lower()

        # Check for high importance indicators
        high_matches = sum(1 for keyword in high_importance_keywords if keyword in content)
        if high_matches > 0:
            score += 0.3 * min(high_matches, 3)

        # Check for medium importance indicators
        medium_matches = sum(1 for keyword in medium_importance_keywords if keyword in content)
        if medium_matches > 0:
            score += 0.2 * min(medium_matches, 2)

        # Check for low importance indicators (negative score)
        low_matches = sum(1 for keyword in low_importance_keywords if keyword in content)
        if low_matches > 0:
            score -= 0.2 * min(low_matches, 2)

        # Attendee count factor
        attendee_count = len(attendees)
        if attendee_count >= 10:
            score += 0.2  # Large meetings are often important
        elif attendee_count <= 2:
            score -= 0.1  # Small meetings might be less critical

        # Meeting organizer importance (simplified)
        organizer = next((att for att in attendees if att.get("organizer")), {})
        organizer_email = organizer.get("email", "")

        # Check if organizer is from important domain or has important title
        important_domains = ["leadership", "exec", "board"]
        if any(domain in organizer_email for domain in important_domains):
            score += 0.2

        return max(0.0, min(1.0, score))

    async def _calculate_conflict_score(
        self,
        start_time: datetime,
        end_time: datetime,
        existing_meetings: List[Meeting],
        user: User
    ) -> float:
        """Calculate conflict score (0.0 to 1.0)"""
        score = 0.0

        # Check for direct time conflicts
        for meeting in existing_meetings:
            if (start_time < meeting.end_time and end_time > meeting.start_time):
                # Direct overlap
                overlap_minutes = min(
                    (min(end_time, meeting.end_time) - max(start_time, meeting.start_time)).total_seconds() / 60,
                    0
                )
                if overlap_minutes > 0:
                    score += 0.5  # Major penalty for direct conflicts

        # Check for back-to-back meetings (no buffer time)
        buffer_minutes = 15
        for meeting in existing_meetings:
            # Meeting right before
            if abs((start_time - meeting.end_time).total_seconds() / 60) <= buffer_minutes:
                score += 0.3

            # Meeting right after
            if abs((meeting.start_time - end_time).total_seconds() / 60) <= buffer_minutes:
                score += 0.3

        # Check if it conflicts with typical focus time
        hour = start_time.hour
        if (9 <= hour <= 11) or (14 <= hour <= 16):  # Focus time blocks
            score += 0.2

        # Check day density (too many meetings)
        day_meetings = [m for m in existing_meetings if m.start_time.date() == start_time.date()]
        if len(day_meetings) >= 6:
            score += 0.3  # High meeting density penalty

        # Check for lunch time conflicts
        if 12 <= hour <= 13:
            score += 0.2

        # Check for early/late meeting times
        if hour < 8 or hour > 18:
            score += 0.3

        return min(1.0, score)

    async def _calculate_productivity_impact(
        self,
        start_time: datetime,
        end_time: datetime,
        title: str,
        user: User
    ) -> float:
        """Calculate productivity impact (-1.0 to 1.0)"""
        impact = 0.0

        # Positive impact indicators
        positive_keywords = [
            "planning", "strategy", "decision", "brainstorm",
            "training", "learning", "development", "skill",
            "client", "customer", "sales", "revenue",
            "productivity", "improvement", "optimization"
        ]

        # Negative impact indicators
        negative_keywords = [
            "status", "update", "sync", "standup",
            "report", "recap", "summary", "info",
            "social", "party", "celebration", "casual"
        ]

        # Neutral indicators
        neutral_keywords = [
            "meeting", "call", "discussion", "review"
        ]

        title_lower = title.lower()

        # Check for positive impact
        positive_matches = sum(1 for keyword in positive_keywords if keyword in title_lower)
        if positive_matches > 0:
            impact += 0.3 * min(positive_matches, 3)

        # Check for negative impact
        negative_matches = sum(1 for keyword in negative_keywords if keyword in title_lower)
        if negative_matches > 0:
            impact -= 0.2 * min(negative_matches, 3)

        # Meeting duration factor
        duration_hours = (end_time - start_time).total_seconds() / 3600
        if duration_hours > 2:
            impact -= 0.2  # Long meetings often less productive
        elif duration_hours < 0.5:
            impact += 0.1  # Short meetings can be efficient

        # Time of day factor
        hour = start_time.hour
        if 9 <= hour <= 11:  # Peak productivity hours
            impact += 0.2
        elif 14 <= hour <= 16:  # Afternoon focus time
            impact += 0.1
        elif hour < 9 or hour > 17:  # Outside normal hours
            impact -= 0.2

        return max(-1.0, min(1.0, impact))

    def _classify_meeting_type(self, title: str, description: str) -> str:
        """Classify meeting type based on title and description"""
        content = f"{title} {description}".lower()

        # Meeting type patterns
        types = {
            "standup": ["standup", "stand-up", "daily", "scrum"],
            "review": ["review", "retrospective", "postmortem", "lessons"],
            "planning": ["planning", "sprint", "roadmap", "strategy", "kickoff"],
            "presentation": ["demo", "presentation", "showcase", "show"],
            "interview": ["interview", "candidate", "hiring", "screening"],
            "training": ["training", "workshop", "learning", "education"],
            "client": ["client", "customer", "external", "vendor"],
            "one-on-one": ["1:1", "one-on-one", "1-on-1", "check-in"],
            "social": ["lunch", "coffee", "social", "team building", "celebration"],
            "decision": ["decision", "approval", "sign-off", "escalation"]
        }

        for meeting_type, keywords in types.items():
            if any(keyword in content for keyword in keywords):
                return meeting_type

        return "general"

    async def _estimate_preparation_time(
        self,
        title: str,
        description: str,
        attendees: List[Dict]
    ) -> int:
        """Estimate preparation time needed in minutes"""
        base_prep = 5  # Base 5 minutes

        content = f"{title} {description}".lower()

        # High prep keywords
        high_prep_keywords = [
            "presentation", "demo", "pitch", "proposal",
            "interview", "review", "audit", "assessment"
        ]

        # Medium prep keywords
        medium_prep_keywords = [
            "planning", "strategy", "brainstorm", "workshop",
            "training", "decision", "client", "customer"
        ]

        high_matches = sum(1 for keyword in high_prep_keywords if keyword in content)
        medium_matches = sum(1 for keyword in medium_prep_keywords if keyword in content)

        if high_matches > 0:
            base_prep = 30  # 30 minutes for high-prep meetings
        elif medium_matches > 0:
            base_prep = 15  # 15 minutes for medium-prep meetings

        # Adjust based on attendee count
        attendee_count = len(attendees)
        if attendee_count >= 10:
            base_prep += 10  # More prep for large meetings

        return base_prep

    async def _suggest_alternatives(
        self,
        start_time: datetime,
        end_time: datetime,
        existing_meetings: List[Meeting]
    ) -> List[Dict[str, Any]]:
        """Suggest alternative meeting times"""
        alternatives = []
        duration = end_time - start_time

        # Get the same day
        target_date = start_time.date()

        # Common good meeting times
        good_times = [
            (10, 0),   # 10:00 AM
            (14, 0),   # 2:00 PM
            (15, 30),  # 3:30 PM
            (11, 0),   # 11:00 AM
            (16, 0),   # 4:00 PM
        ]

        for hour, minute in good_times:
            alt_start = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            alt_start = alt_start.replace(tzinfo=timezone.utc)
            alt_end = alt_start + duration

            # Skip if this is the original time
            if alt_start == start_time:
                continue

            # Check if this time conflicts with existing meetings
            conflicts = False
            for meeting in existing_meetings:
                if (alt_start < meeting.end_time and alt_end > meeting.start_time):
                    conflicts = True
                    break

            if not conflicts:
                alternatives.append({
                    "start_time": alt_start.isoformat(),
                    "end_time": alt_end.isoformat(),
                    "reason": f"Better time slot at {hour:02d}:{minute:02d}",
                    "score": 0.8  # Good alternative score
                })

        # Try next day if no alternatives found
        if not alternatives:
            next_day = target_date + timedelta(days=1)
            for hour, minute in good_times[:3]:  # Try fewer times for next day
                alt_start = datetime.combine(next_day, datetime.min.time().replace(hour=hour, minute=minute))
                alt_start = alt_start.replace(tzinfo=timezone.utc)
                alt_end = alt_start + duration

                alternatives.append({
                    "start_time": alt_start.isoformat(),
                    "end_time": alt_end.isoformat(),
                    "reason": f"Move to next day at {hour:02d}:{minute:02d}",
                    "score": 0.6  # Lower score for different day
                })

        return alternatives[:3]  # Return top 3 alternatives

    async def _make_ai_decision(
        self,
        analysis: Dict[str, Any],
        user: User
    ) -> Dict[str, Any]:
        """Make AI decision based on analysis"""
        importance = analysis["importance_score"]
        conflict = analysis["conflict_score"]
        productivity_impact = analysis["productivity_impact"]

        # Decision logic
        decision_type = AIDecisionType.AUTO_ACCEPT
        confidence = 0.5
        reasoning = "Default acceptance"

        # High conflict situations
        if conflict > 0.7:
            if importance < 0.3:
                decision_type = AIDecisionType.AUTO_DECLINE
                confidence = 0.9
                reasoning = "High conflict, low importance - auto-declining to protect calendar"
            elif len(analysis.get("alternatives", [])) > 0:
                decision_type = AIDecisionType.SUGGEST_RESCHEDULE
                confidence = 0.8
                reasoning = "High conflict detected - suggesting reschedule to better time"
            else:
                decision_type = AIDecisionType.REQUEST_MORE_INFO
                confidence = 0.6
                reasoning = "High conflict but important meeting - requesting more context"

        # Low importance meetings
        elif importance < 0.2:
            if productivity_impact < -0.3:
                decision_type = AIDecisionType.AUTO_DECLINE
                confidence = 0.8
                reasoning = "Low importance with negative productivity impact"
            else:
                decision_type = AIDecisionType.DELEGATE
                confidence = 0.7
                reasoning = "Low importance - could potentially be delegated"

        # High importance meetings
        elif importance > 0.8:
            decision_type = AIDecisionType.AUTO_ACCEPT
            confidence = 0.9
            reasoning = "High importance meeting - auto-accepting"

        # Medium importance with good productivity impact
        elif importance > 0.5 and productivity_impact > 0.3:
            decision_type = AIDecisionType.AUTO_ACCEPT
            confidence = 0.8
            reasoning = "Good importance and positive productivity impact"

        return {
            "type": decision_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "auto_actions": await self._suggest_auto_actions(decision_type, analysis)
        }

    async def _suggest_auto_actions(
        self,
        decision_type: AIDecisionType,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest automatic actions based on decision"""
        actions = []

        if decision_type == AIDecisionType.AUTO_ACCEPT:
            prep_time = analysis.get("required_preparation", 5)
            if prep_time > 10:
                actions.append({
                    "type": "create_prep_time",
                    "description": f"Block {prep_time} minutes before meeting for preparation",
                    "parameters": {"minutes": prep_time}
                })

            actions.append({
                "type": "create_buffer",
                "description": "Add 5-minute buffer after meeting",
                "parameters": {"minutes": 5}
            })

        elif decision_type == AIDecisionType.SUGGEST_RESCHEDULE:
            alternatives = analysis.get("alternatives", [])
            if alternatives:
                actions.append({
                    "type": "suggest_reschedule",
                    "description": f"Suggest alternative time: {alternatives[0]['reason']}",
                    "parameters": {"alternative": alternatives[0]}
                })

        elif decision_type == AIDecisionType.AUTO_DECLINE:
            actions.append({
                "type": "auto_decline",
                "description": "Automatically decline with professional message",
                "parameters": {"reason": analysis["ai_decision"]["reasoning"]}
            })

        return actions

    async def _get_user_meetings_for_period(
        self,
        user: User,
        db: AsyncSession,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> List[Meeting]:
        """Get user's meetings for a specific time period"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        result = await db.execute(
            select(Meeting).where(
                and_(
                    Meeting.user_id == user.id,
                    Meeting.start_time >= start_datetime,
                    Meeting.start_time <= end_datetime
                )
            )
        )

        return result.scalars().all()

    async def execute_autonomous_actions(
        self,
        user: User,
        meeting_data: Dict[str, Any],
        ai_decision: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Execute autonomous actions based on AI decision"""
        results = {
            "executed_actions": [],
            "failed_actions": [],
            "success": False
        }

        try:
            access_token = await self.oauth_service.get_valid_access_token(user, db)
            if not access_token:
                results["failed_actions"].append("No valid access token")
                return results

            event_id = meeting_data.get("id")
            auto_actions = ai_decision.get("auto_actions", [])

            for action in auto_actions:
                try:
                    if action["type"] == "auto_decline":
                        success = await self.autonomous_manager.auto_decline_meeting(
                            access_token,
                            event_id,
                            action["parameters"].get("reason"),
                            "primary"
                        )
                        if success:
                            results["executed_actions"].append(f"Auto-declined meeting: {action['description']}")
                        else:
                            results["failed_actions"].append(f"Failed to auto-decline: {action['description']}")

                    elif action["type"] == "create_prep_time":
                        prep_minutes = action["parameters"]["minutes"]
                        buffer_events = await self.autonomous_manager.create_buffer_time(
                            access_token,
                            before_event_id=event_id,
                            buffer_minutes=prep_minutes,
                            calendar_id="primary"
                        )
                        if buffer_events:
                            results["executed_actions"].append(f"Created prep time: {action['description']}")
                        else:
                            results["failed_actions"].append(f"Failed to create prep time: {action['description']}")

                    elif action["type"] == "create_buffer":
                        buffer_minutes = action["parameters"]["minutes"]
                        buffer_events = await self.autonomous_manager.create_buffer_time(
                            access_token,
                            after_event_id=event_id,
                            buffer_minutes=buffer_minutes,
                            calendar_id="primary"
                        )
                        if buffer_events:
                            results["executed_actions"].append(f"Created buffer time: {action['description']}")
                        else:
                            results["failed_actions"].append(f"Failed to create buffer: {action['description']}")

                    elif action["type"] == "suggest_reschedule":
                        # For demo purposes, we'll just log the suggestion
                        # In production, this would send a message to organizer
                        alternative = action["parameters"]["alternative"]
                        results["executed_actions"].append(
                            f"Suggested reschedule: {action['description']} to {alternative['start_time']}"
                        )

                except Exception as e:
                    logger.error(f"Failed to execute action {action['type']}: {e}")
                    results["failed_actions"].append(f"Action {action['type']}: {str(e)}")

            results["success"] = len(results["executed_actions"]) > 0
            return results

        except Exception as e:
            logger.error(f"Error executing autonomous actions: {e}")
            results["failed_actions"].append(f"General error: {str(e)}")
            return results


# Global instance
meeting_intelligence_service = MeetingIntelligenceService()