"""
Advanced LLM-powered Meeting Analysis Engine
Provides sophisticated AI analysis for meetings using state-of-the-art language models
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import openai
from openai import AsyncOpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class AnalysisDepth(Enum):
    """Different levels of analysis depth"""
    QUICK = "quick"  # Fast, surface-level analysis
    STANDARD = "standard"  # Balanced analysis
    DEEP = "deep"  # Comprehensive, multi-faceted analysis
    EXECUTIVE = "executive"  # Executive-level strategic analysis


class MeetingCategory(Enum):
    """Categories of meetings based on analysis"""
    STATUS_UPDATE = "status_update"
    BRAINSTORMING = "brainstorming"
    DECISION_MAKING = "decision_making"
    ONE_ON_ONE = "one_on_one"
    TRAINING = "training"
    CLIENT_MEETING = "client_meeting"
    TEAM_BUILDING = "team_building"
    REVIEW = "review"
    PLANNING = "planning"
    EMERGENCY = "emergency"
    SOCIAL = "social"
    UNKNOWN = "unknown"


@dataclass
class MeetingInsight:
    """Comprehensive meeting insights from AI analysis"""
    importance_score: float  # 0.0 to 10.0
    urgency_score: float  # 0.0 to 10.0
    ai_attendance_suitable: bool
    ai_confidence: float  # 0.0 to 1.0
    category: MeetingCategory
    key_topics: List[str]
    required_preparation: List[str]
    expected_outcomes: List[str]
    decision_points: List[str]
    attendee_analysis: Dict[str, str]  # email -> role/importance
    optimal_duration_minutes: int
    efficiency_recommendations: List[str]
    potential_blockers: List[str]
    follow_up_actions: List[str]
    sentiment_analysis: Dict[str, float]  # positive, neutral, negative scores
    strategic_value: str  # High/Medium/Low with explanation
    skip_probability: float  # 0.0 to 1.0
    delegation_candidates: List[str]
    alternative_approaches: List[str]
    generated_summary: str
    ai_reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            **asdict(self),
            'category': self.category.value
        }


class LLMAnalyzer:
    """Advanced LLM-powered meeting analyzer"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
            logger.warning("No OpenAI API key provided. LLM features will be limited.")

        # Initialize TF-IDF vectorizer for similarity analysis
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.meeting_patterns_cache = {}

        # Pre-defined prompt templates for consistency
        self.prompt_templates = self._initialize_prompt_templates()

    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize sophisticated prompt templates"""
        return {
            "meeting_analysis": """
                You are an elite executive assistant AI with expertise in time management and meeting optimization.
                Analyze this meeting with surgical precision:

                Meeting Title: {title}
                Description: {description}
                Duration: {duration} minutes
                Attendees: {attendees}
                Organizer: {organizer}
                Time: {meeting_time}
                Location/Link: {location}

                Provide a comprehensive analysis in JSON format:
                {{
                    "importance_score": <0-10, based on strategic value>,
                    "urgency_score": <0-10, based on time sensitivity>,
                    "category": "<meeting category>",
                    "ai_attendance_suitable": <true if AI can represent the user>,
                    "key_topics": [<3-5 main discussion points>],
                    "required_preparation": [<specific prep items>],
                    "expected_outcomes": [<concrete deliverables>],
                    "decision_points": [<decisions to be made>],
                    "optimal_duration_minutes": <recommended duration>,
                    "efficiency_recommendations": [<ways to improve meeting>],
                    "potential_blockers": [<risks or issues>],
                    "skip_probability": <0-1, likelihood user can skip>,
                    "delegation_candidates": [<who else could attend>],
                    "alternative_approaches": [<other ways to achieve goals>],
                    "strategic_value": "<High/Medium/Low> - <explanation>",
                    "ai_reasoning": "<detailed reasoning for recommendations>"
                }}

                Consider factors like: ROI of attendance, alternative communication methods,
                meeting fatigue, focus time protection, and strategic alignment.
            """,

            "attendee_analysis": """
                Analyze the importance and roles of meeting attendees:

                Meeting: {title}
                Attendees: {attendees}
                User: {user_email}
                Context: {context}

                For each attendee, determine:
                1. Their likely role in the meeting
                2. Their decision-making authority
                3. Whether they are required or optional
                4. Their relationship to the user

                Return JSON with email as key and analysis as value.
            """,

            "calendar_pattern_recognition": """
                You are a calendar optimization expert. Analyze these calendar patterns:

                Recent Meetings: {recent_meetings}
                Upcoming Schedule: {upcoming_schedule}
                User Preferences: {preferences}

                Identify:
                1. Recurring meeting patterns and their effectiveness
                2. Meeting clustering and fatigue zones
                3. Optimal focus time slots
                4. Inefficient meeting patterns
                5. Opportunities for batch processing
                6. Recommended schedule optimizations

                Provide actionable insights for calendar optimization.
            """,

            "natural_explanation": """
                Generate a natural, conversational explanation for this meeting decision:

                Decision: {decision}
                Meeting: {meeting_title}
                Reasoning Data: {reasoning_data}
                User Context: {user_context}

                Write a 2-3 sentence explanation that:
                1. Sounds human and empathetic
                2. Clearly explains the reasoning
                3. Provides actionable next steps
                4. Maintains professional tone with personality

                Format: Conversational but professional explanation.
            """,

            "meeting_summary": """
                Create an executive summary for this meeting:

                Meeting Details: {meeting_details}
                Analysis Results: {analysis_results}

                Generate:
                1. One-line executive summary
                2. Key preparation points (bullet list)
                3. Critical decisions to be made
                4. Post-meeting action items template
                5. Success metrics

                Keep it concise and actionable.
            """,

            "personality_prompt": """
                You are embodying the {personality_type} AI assistant personality.

                Personality Traits: {traits}
                Communication Style: {style}

                Based on this personality, make a decision about:
                Meeting: {meeting_title}
                Context: {context}
                Constraints: {constraints}

                Respond in character with a decision and explanation that reflects
                this personality's approach to time management and collaboration.
            """
        }

    async def analyze_meeting(
        self,
        meeting_data: Dict[str, Any],
        depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_context: Optional[Dict[str, Any]] = None
    ) -> MeetingInsight:
        """
        Perform comprehensive AI analysis of a meeting
        """
        try:
            # Extract meeting details
            title = meeting_data.get("title", "")
            description = meeting_data.get("description", "")
            attendees = meeting_data.get("attendees", [])
            duration = meeting_data.get("duration_minutes", 30)
            organizer = meeting_data.get("organizer_email", "")
            meeting_time = meeting_data.get("start_time", "")
            location = meeting_data.get("location", meeting_data.get("meeting_link", ""))

            if self.client and depth != AnalysisDepth.QUICK:
                # Use LLM for deep analysis
                insight = await self._llm_deep_analysis(
                    title, description, attendees, duration,
                    organizer, meeting_time, location, depth, user_context
                )
            else:
                # Use rule-based analysis for quick or no-API scenarios
                insight = self._rule_based_analysis(
                    title, description, attendees, duration,
                    organizer, meeting_time, location
                )

            # Enhance with pattern recognition
            insight = await self._enhance_with_patterns(insight, meeting_data, user_context)

            # Cache patterns for learning
            self._update_pattern_cache(meeting_data, insight)

            return insight

        except Exception as e:
            logger.error(f"Error analyzing meeting: {e}")
            # Return basic analysis on error
            return self._fallback_analysis(meeting_data)

    async def _llm_deep_analysis(
        self,
        title: str,
        description: str,
        attendees: List[str],
        duration: int,
        organizer: str,
        meeting_time: str,
        location: str,
        depth: AnalysisDepth,
        user_context: Optional[Dict[str, Any]]
    ) -> MeetingInsight:
        """Perform deep LLM-based analysis"""

        # Prepare the analysis prompt
        prompt = self.prompt_templates["meeting_analysis"].format(
            title=title,
            description=description or "No description provided",
            duration=duration,
            attendees=", ".join(attendees) if attendees else "Unknown",
            organizer=organizer,
            meeting_time=meeting_time,
            location=location or "Not specified"
        )

        # Add user context if available
        if user_context:
            prompt += f"\n\nUser Context: {json.dumps(user_context, indent=2)}"

        try:
            # Make LLM call with appropriate model based on depth
            model = "gpt-4o" if depth == AnalysisDepth.DEEP else "gpt-4o-mini"

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert meeting analyst. Provide analysis in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistent analysis
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)

            # Perform attendee analysis if depth is DEEP or EXECUTIVE
            attendee_roles = {}
            if depth in [AnalysisDepth.DEEP, AnalysisDepth.EXECUTIVE]:
                attendee_roles = await self._analyze_attendees(
                    title, attendees, user_context
                )

            # Generate natural language summary
            summary = await self._generate_summary(title, analysis)

            # Calculate sentiment (simplified for now)
            sentiment = self._analyze_sentiment(description, title)

            return MeetingInsight(
                importance_score=float(analysis.get("importance_score", 5)),
                urgency_score=float(analysis.get("urgency_score", 5)),
                ai_attendance_suitable=analysis.get("ai_attendance_suitable", False),
                ai_confidence=0.85,  # High confidence for LLM analysis
                category=self._parse_category(analysis.get("category", "unknown")),
                key_topics=analysis.get("key_topics", []),
                required_preparation=analysis.get("required_preparation", []),
                expected_outcomes=analysis.get("expected_outcomes", []),
                decision_points=analysis.get("decision_points", []),
                attendee_analysis=attendee_roles,
                optimal_duration_minutes=analysis.get("optimal_duration_minutes", duration),
                efficiency_recommendations=analysis.get("efficiency_recommendations", []),
                potential_blockers=analysis.get("potential_blockers", []),
                follow_up_actions=analysis.get("follow_up_actions", []),
                sentiment_analysis=sentiment,
                strategic_value=analysis.get("strategic_value", "Medium - Standard meeting"),
                skip_probability=float(analysis.get("skip_probability", 0.3)),
                delegation_candidates=analysis.get("delegation_candidates", []),
                alternative_approaches=analysis.get("alternative_approaches", []),
                generated_summary=summary,
                ai_reasoning=analysis.get("ai_reasoning", "")
            )

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fall back to rule-based analysis
            return self._rule_based_analysis(
                title, description, attendees, duration,
                organizer, meeting_time, location
            )

    def _rule_based_analysis(
        self,
        title: str,
        description: str,
        attendees: List[str],
        duration: int,
        organizer: str,
        meeting_time: str,
        location: str
    ) -> MeetingInsight:
        """Rule-based analysis when LLM is not available"""

        # Keyword-based importance scoring
        title_lower = title.lower()
        desc_lower = (description or "").lower()
        combined_text = f"{title_lower} {desc_lower}"

        # Calculate importance based on keywords
        high_importance_keywords = ["urgent", "critical", "emergency", "escalation",
                                   "decision", "approval", "budget", "strategic",
                                   "executive", "board", "client", "customer"]

        low_importance_keywords = ["optional", "fun", "social", "casual", "catch-up",
                                   "standup", "sync", "check-in", "status"]

        importance_score = 5.0
        for keyword in high_importance_keywords:
            if keyword in combined_text:
                importance_score = min(10, importance_score + 1.5)

        for keyword in low_importance_keywords:
            if keyword in combined_text:
                importance_score = max(0, importance_score - 1)

        # Urgency based on time
        urgency_score = 5.0
        if "urgent" in combined_text or "asap" in combined_text:
            urgency_score = 9.0
        elif "emergency" in combined_text:
            urgency_score = 10.0

        # Determine if AI can attend
        ai_suitable_meetings = ["status", "update", "standup", "review", "sync"]
        ai_attendance_suitable = any(keyword in title_lower for keyword in ai_suitable_meetings)

        # Categorize meeting
        category = self._categorize_meeting(title, description)

        # Optimal duration based on meeting type
        optimal_duration = self._calculate_optimal_duration(category, attendees, duration)

        # Skip probability
        skip_probability = 0.3
        if importance_score < 4:
            skip_probability = 0.7
        elif importance_score > 7:
            skip_probability = 0.1

        # Generate basic recommendations
        efficiency_recommendations = []
        if duration > optimal_duration:
            efficiency_recommendations.append(f"Consider reducing to {optimal_duration} minutes")
        if len(attendees) > 8:
            efficiency_recommendations.append("Large meeting - consider splitting or reducing attendees")

        return MeetingInsight(
            importance_score=importance_score,
            urgency_score=urgency_score,
            ai_attendance_suitable=ai_attendance_suitable,
            ai_confidence=0.6,  # Lower confidence for rule-based
            category=category,
            key_topics=self._extract_topics(title, description),
            required_preparation=["Review meeting agenda", "Prepare relevant documents"],
            expected_outcomes=["Action items defined", "Next steps identified"],
            decision_points=[],
            attendee_analysis={},
            optimal_duration_minutes=optimal_duration,
            efficiency_recommendations=efficiency_recommendations,
            potential_blockers=["Unclear agenda"] if not description else [],
            follow_up_actions=["Send meeting notes", "Update action items"],
            sentiment_analysis={"positive": 0.33, "neutral": 0.34, "negative": 0.33},
            strategic_value="Medium - Standard operational meeting",
            skip_probability=skip_probability,
            delegation_candidates=[],
            alternative_approaches=["Email update", "Async discussion"] if ai_attendance_suitable else [],
            generated_summary=f"{title} - {duration} minute meeting with {len(attendees)} attendees",
            ai_reasoning="Rule-based analysis due to LLM unavailability"
        )

    def _categorize_meeting(self, title: str, description: str) -> MeetingCategory:
        """Categorize meeting based on title and description"""
        text = f"{title} {description or ''}".lower()

        category_keywords = {
            MeetingCategory.STATUS_UPDATE: ["status", "update", "standup", "sync"],
            MeetingCategory.BRAINSTORMING: ["brainstorm", "ideation", "creative", "workshop"],
            MeetingCategory.DECISION_MAKING: ["decision", "approval", "review", "gate"],
            MeetingCategory.ONE_ON_ONE: ["1:1", "one-on-one", "1-on-1", "catch up"],
            MeetingCategory.TRAINING: ["training", "learning", "onboarding", "tutorial"],
            MeetingCategory.CLIENT_MEETING: ["client", "customer", "prospect", "sales"],
            MeetingCategory.TEAM_BUILDING: ["team building", "social", "happy hour", "lunch"],
            MeetingCategory.REVIEW: ["review", "retrospective", "retro", "post-mortem"],
            MeetingCategory.PLANNING: ["planning", "roadmap", "strategy", "sprint"],
            MeetingCategory.EMERGENCY: ["emergency", "urgent", "critical", "incident"]
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category

        return MeetingCategory.UNKNOWN

    def _calculate_optimal_duration(
        self,
        category: MeetingCategory,
        attendees: List[str],
        current_duration: int
    ) -> int:
        """Calculate optimal meeting duration"""

        # Base durations by category
        category_durations = {
            MeetingCategory.STATUS_UPDATE: 15,
            MeetingCategory.BRAINSTORMING: 60,
            MeetingCategory.DECISION_MAKING: 30,
            MeetingCategory.ONE_ON_ONE: 30,
            MeetingCategory.TRAINING: 60,
            MeetingCategory.CLIENT_MEETING: 45,
            MeetingCategory.TEAM_BUILDING: 60,
            MeetingCategory.REVIEW: 45,
            MeetingCategory.PLANNING: 90,
            MeetingCategory.EMERGENCY: 30,
            MeetingCategory.UNKNOWN: 30
        }

        base_duration = category_durations.get(category, 30)

        # Adjust based on number of attendees
        if len(attendees) > 5:
            base_duration = int(base_duration * 1.2)
        if len(attendees) > 10:
            base_duration = int(base_duration * 1.4)

        # Don't exceed current duration by too much
        return min(base_duration, max(15, current_duration))

    def _extract_topics(self, title: str, description: str) -> List[str]:
        """Extract key topics from title and description"""
        text = f"{title} {description or ''}"

        # Simple keyword extraction (in production, use NLP libraries)
        words = text.split()
        # Filter common words and extract meaningful terms
        topics = []
        important_words = [w for w in words if len(w) > 4 and w.lower() not in
                          ['meeting', 'discuss', 'about', 'with', 'from', 'this', 'that']]

        return important_words[:5]  # Return top 5 topics

    def _analyze_sentiment(self, description: str, title: str) -> Dict[str, float]:
        """Analyze sentiment of meeting description"""
        text = f"{title} {description or ''}".lower()

        positive_words = ["great", "excellent", "opportunity", "success", "celebrate",
                         "achievement", "progress", "innovative"]
        negative_words = ["problem", "issue", "concern", "risk", "failure", "delay",
                         "escalation", "urgent", "critical"]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        total = max(1, positive_count + negative_count)

        if total == 0:
            return {"positive": 0.33, "neutral": 0.34, "negative": 0.33}

        positive_score = positive_count / total
        negative_score = negative_count / total
        neutral_score = max(0, 1.0 - positive_score - negative_score)

        return {
            "positive": round(positive_score, 2),
            "neutral": round(neutral_score, 2),
            "negative": round(negative_score, 2)
        }

    def _parse_category(self, category_str: str) -> MeetingCategory:
        """Parse category string to enum"""
        category_map = {
            "status_update": MeetingCategory.STATUS_UPDATE,
            "status": MeetingCategory.STATUS_UPDATE,
            "brainstorming": MeetingCategory.BRAINSTORMING,
            "decision": MeetingCategory.DECISION_MAKING,
            "one_on_one": MeetingCategory.ONE_ON_ONE,
            "1:1": MeetingCategory.ONE_ON_ONE,
            "training": MeetingCategory.TRAINING,
            "client": MeetingCategory.CLIENT_MEETING,
            "team_building": MeetingCategory.TEAM_BUILDING,
            "review": MeetingCategory.REVIEW,
            "planning": MeetingCategory.PLANNING,
            "emergency": MeetingCategory.EMERGENCY
        }

        return category_map.get(category_str.lower().replace(" ", "_"), MeetingCategory.UNKNOWN)

    async def _analyze_attendees(
        self,
        title: str,
        attendees: List[str],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Analyze attendee roles and importance"""

        if not self.client or not attendees:
            return {}

        prompt = self.prompt_templates["attendee_analysis"].format(
            title=title,
            attendees=json.dumps(attendees),
            user_email=user_context.get("user_email", "") if user_context else "",
            context=json.dumps(user_context) if user_context else "{}"
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Analyze meeting attendees and return JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Attendee analysis failed: {e}")
            return {attendee: "Participant" for attendee in attendees}

    async def _generate_summary(self, title: str, analysis: Dict[str, Any]) -> str:
        """Generate natural language summary"""

        if not self.client:
            return f"{title} - Meeting analyzed with importance score {analysis.get('importance_score', 5)}/10"

        prompt = self.prompt_templates["meeting_summary"].format(
            meeting_details=title,
            analysis_results=json.dumps(analysis, indent=2)
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate concise meeting summary."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"{title} - Importance: {analysis.get('importance_score', 5)}/10"

    async def _enhance_with_patterns(
        self,
        insight: MeetingInsight,
        meeting_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> MeetingInsight:
        """Enhance insights with pattern recognition"""

        # Check for recurring meeting patterns
        if user_context and "recent_meetings" in user_context:
            similar_meetings = self._find_similar_meetings(
                meeting_data,
                user_context["recent_meetings"]
            )

            if similar_meetings:
                # Adjust recommendations based on patterns
                avg_duration = np.mean([m.get("duration_minutes", 30) for m in similar_meetings])
                if abs(avg_duration - insight.optimal_duration_minutes) > 15:
                    insight.optimal_duration_minutes = int(avg_duration)
                    insight.efficiency_recommendations.append(
                        f"Based on history, {int(avg_duration)} minutes is typical for this meeting type"
                    )

        return insight

    def _find_similar_meetings(
        self,
        current_meeting: Dict[str, Any],
        recent_meetings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find similar meetings based on title and attendees"""

        if not recent_meetings:
            return []

        current_title = current_meeting.get("title", "")
        current_attendees = set(current_meeting.get("attendees", []))

        similar = []
        for meeting in recent_meetings:
            title_similarity = self._calculate_text_similarity(
                current_title,
                meeting.get("title", "")
            )

            meeting_attendees = set(meeting.get("attendees", []))
            attendee_overlap = len(current_attendees & meeting_attendees) / max(
                len(current_attendees | meeting_attendees), 1
            )

            # Consider similar if title is >70% similar or attendees >60% overlap
            if title_similarity > 0.7 or attendee_overlap > 0.6:
                similar.append(meeting)

        return similar

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""

        if not text1 or not text2:
            return 0.0

        # Simple character-based similarity
        # In production, use better NLP similarity measures
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        if text1_lower == text2_lower:
            return 1.0

        # Calculate Jaccard similarity of words
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _update_pattern_cache(self, meeting_data: Dict[str, Any], insight: MeetingInsight):
        """Update pattern cache for learning"""

        key = f"{meeting_data.get('title', '')}_{insight.category.value}"

        if key not in self.meeting_patterns_cache:
            self.meeting_patterns_cache[key] = []

        self.meeting_patterns_cache[key].append({
            "timestamp": datetime.utcnow().isoformat(),
            "importance": insight.importance_score,
            "duration": meeting_data.get("duration_minutes", 30),
            "skip_probability": insight.skip_probability,
            "ai_suitable": insight.ai_attendance_suitable
        })

        # Keep only recent patterns (last 50)
        if len(self.meeting_patterns_cache[key]) > 50:
            self.meeting_patterns_cache[key] = self.meeting_patterns_cache[key][-50:]

    def _fallback_analysis(self, meeting_data: Dict[str, Any]) -> MeetingInsight:
        """Minimal fallback analysis when everything else fails"""

        return MeetingInsight(
            importance_score=5.0,
            urgency_score=5.0,
            ai_attendance_suitable=False,
            ai_confidence=0.3,
            category=MeetingCategory.UNKNOWN,
            key_topics=[],
            required_preparation=["Review meeting details"],
            expected_outcomes=["Meeting completion"],
            decision_points=[],
            attendee_analysis={},
            optimal_duration_minutes=meeting_data.get("duration_minutes", 30),
            efficiency_recommendations=["Unable to analyze - manual review recommended"],
            potential_blockers=["Analysis unavailable"],
            follow_up_actions=[],
            sentiment_analysis={"positive": 0.33, "neutral": 0.34, "negative": 0.33},
            strategic_value="Unknown - Manual review required",
            skip_probability=0.5,
            delegation_candidates=[],
            alternative_approaches=[],
            generated_summary="Meeting analysis unavailable",
            ai_reasoning="Fallback analysis due to system error"
        )

    async def generate_natural_explanation(
        self,
        decision: str,
        meeting_title: str,
        reasoning_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate natural language explanation for decisions"""

        if not self.client:
            return f"I've decided to {decision} the meeting '{meeting_title}' based on its importance and your schedule."

        prompt = self.prompt_templates["natural_explanation"].format(
            decision=decision,
            meeting_title=meeting_title,
            reasoning_data=json.dumps(reasoning_data, indent=2),
            user_context=json.dumps(user_context) if user_context else "{}"
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate natural, conversational explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return f"I've decided to {decision} '{meeting_title}' to optimize your schedule."

    async def analyze_calendar_patterns(
        self,
        recent_meetings: List[Dict[str, Any]],
        upcoming_schedule: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze calendar patterns for optimization opportunities"""

        if not self.client:
            return self._basic_pattern_analysis(recent_meetings, upcoming_schedule)

        prompt = self.prompt_templates["calendar_pattern_recognition"].format(
            recent_meetings=json.dumps(recent_meetings[:20], indent=2),  # Limit to recent 20
            upcoming_schedule=json.dumps(upcoming_schedule[:20], indent=2),
            preferences=json.dumps(user_preferences) if user_preferences else "{}"
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a calendar optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            analysis_text = response.choices[0].message.content

            # Parse structured insights from the response
            return self._parse_pattern_insights(analysis_text, recent_meetings, upcoming_schedule)

        except Exception as e:
            logger.error(f"Calendar pattern analysis failed: {e}")
            return self._basic_pattern_analysis(recent_meetings, upcoming_schedule)

    def _basic_pattern_analysis(
        self,
        recent_meetings: List[Dict[str, Any]],
        upcoming_schedule: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Basic pattern analysis without LLM"""

        # Calculate basic statistics
        total_meetings = len(recent_meetings) + len(upcoming_schedule)
        avg_duration = np.mean([m.get("duration_minutes", 30) for m in recent_meetings]) if recent_meetings else 30

        # Find meeting clusters
        meeting_hours = [datetime.fromisoformat(m.get("start_time", "")).hour
                        for m in recent_meetings if m.get("start_time")]

        peak_hours = []
        if meeting_hours:
            from collections import Counter
            hour_counts = Counter(meeting_hours)
            peak_hours = [hour for hour, count in hour_counts.most_common(3)]

        return {
            "patterns": {
                "total_meetings": total_meetings,
                "average_duration": avg_duration,
                "peak_meeting_hours": peak_hours,
                "meeting_density": total_meetings / 7 if total_meetings else 0  # per day
            },
            "recommendations": [
                "Consider batching similar meetings",
                "Protect focus time in the morning",
                "Implement meeting-free blocks"
            ],
            "optimization_opportunities": [
                "Reduce average meeting duration",
                "Consolidate status updates",
                "Convert some meetings to async updates"
            ]
        }

    def _parse_pattern_insights(
        self,
        analysis_text: str,
        recent_meetings: List[Dict[str, Any]],
        upcoming_schedule: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse pattern insights from LLM response"""

        # Extract key insights using simple parsing
        # In production, use structured output format

        insights = {
            "patterns": {},
            "recommendations": [],
            "optimization_opportunities": [],
            "focus_time_suggestions": [],
            "meeting_reduction_targets": []
        }

        # Parse recommendations (looking for bullet points or numbered lists)
        lines = analysis_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if "recommendation" in line.lower():
                current_section = "recommendations"
            elif "optimization" in line.lower() or "opportunit" in line.lower():
                current_section = "optimization_opportunities"
            elif "focus" in line.lower():
                current_section = "focus_time_suggestions"
            elif line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                # Extract bullet points
                clean_line = re.sub(r'^[•\-\*\d\.]\s*', '', line)
                if current_section and current_section in insights:
                    if isinstance(insights[current_section], list):
                        insights[current_section].append(clean_line)

        return insights