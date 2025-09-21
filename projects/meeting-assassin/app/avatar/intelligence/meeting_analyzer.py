"""
Meeting Intelligence and Analytics System
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import numpy as np
from collections import Counter, defaultdict
import re
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


@dataclass
class MeetingMetrics:
    """Meeting performance metrics"""
    participation_balance: float  # 0-1, 1 being perfectly balanced
    engagement_level: float  # 0-1, overall engagement
    decision_velocity: float  # decisions per minute
    topic_coherence: float  # 0-1, how focused the discussion is
    sentiment_score: float  # -1 to 1, negative to positive
    productivity_score: float  # 0-1, overall productivity


@dataclass
class SpeakerAnalytics:
    """Analytics for individual speakers"""
    speaker_id: str
    speaking_time: float  # seconds
    word_count: int
    interruptions: int
    questions_asked: int
    decisions_proposed: int
    sentiment_average: float
    engagement_score: float


@dataclass
class TopicAnalysis:
    """Analysis of discussed topics"""
    topic: str
    duration: float  # minutes
    speakers: List[str]
    sentiment: float
    decisions: List[str]
    action_items: List[str]
    key_points: List[str]


class MeetingAnalyzer:
    """
    Advanced meeting analysis and intelligence engine
    """

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize meeting analyzer"""
        self.openai_client = openai_client

        # Analysis state
        self.current_analysis: Dict[str, Any] = {}
        self.speaker_profiles: Dict[str, SpeakerAnalytics] = {}
        self.topics_timeline: List[Tuple[float, str]] = []
        self.sentiment_history: List[Tuple[float, float]] = []

        # Patterns for detection
        self.decision_patterns = [
            r"we (should|will|must|need to)",
            r"let's (go with|proceed|do)",
            r"(agreed|decided|confirmed)",
            r"the decision is",
            r"we've decided"
        ]

        self.action_patterns = [
            r"(I|you|we|they) will",
            r"action item:",
            r"todo:",
            r"by (monday|tuesday|wednesday|thursday|friday|next week|end of)",
            r"responsible:",
            r"owner:"
        ]

        self.question_patterns = [
            r"\?$",
            r"^(what|why|how|when|where|who|which)",
            r"(can|could|would|should) (you|we|I)",
            r"thoughts on",
            r"opinion about"
        ]

    async def analyze_meeting(
        self,
        transcript: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive meeting analysis"""
        try:
            # Basic statistics
            stats = self._calculate_basic_stats(transcript)

            # Speaker analytics
            speaker_analytics = self._analyze_speakers(transcript)

            # Topic analysis
            topics = await self._analyze_topics(transcript)

            # Sentiment analysis
            sentiment = await self._analyze_sentiment(transcript)

            # Extract insights
            insights = await self._extract_insights(transcript, stats)

            # Calculate metrics
            metrics = self._calculate_metrics(stats, speaker_analytics)

            # Identify patterns
            patterns = self._identify_patterns(transcript)

            return {
                "statistics": stats,
                "speakers": speaker_analytics,
                "topics": topics,
                "sentiment": sentiment,
                "metrics": metrics,
                "insights": insights,
                "patterns": patterns,
                "phase": self._determine_meeting_phase(transcript),
                "action_items": await self._extract_action_items(transcript),
                "decisions": await self._extract_decisions(transcript) if not decisions else decisions,
                "key_moments": self._identify_key_moments(transcript)
            }

        except Exception as e:
            logger.error(f"Meeting analysis error: {e}")
            return {}

    def _calculate_basic_stats(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic meeting statistics"""
        if not transcript:
            return {}

        total_words = sum(len(entry.get("text", "").split()) for entry in transcript)
        speakers = list(set(entry.get("speaker", "Unknown") for entry in transcript))
        duration = self._estimate_duration(transcript)

        return {
            "total_statements": len(transcript),
            "total_words": total_words,
            "unique_speakers": len(speakers),
            "duration_minutes": duration,
            "avg_statement_length": total_words / len(transcript) if transcript else 0,
            "words_per_minute": total_words / duration if duration > 0 else 0
        }

    def _analyze_speakers(self, transcript: List[Dict[str, Any]]) -> List[SpeakerAnalytics]:
        """Analyze individual speaker contributions"""
        speaker_data = defaultdict(lambda: {
            "words": 0,
            "statements": 0,
            "questions": 0,
            "interruptions": 0,
            "sentiment_sum": 0.0,
            "last_timestamp": None
        })

        for i, entry in enumerate(transcript):
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("text", "")

            speaker_data[speaker]["words"] += len(text.split())
            speaker_data[speaker]["statements"] += 1

            # Check for questions
            if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.question_patterns):
                speaker_data[speaker]["questions"] += 1

            # Simple interruption detection
            if i > 0 and transcript[i-1].get("speaker") != speaker:
                prev_text = transcript[i-1].get("text", "")
                if len(prev_text.split()) < 10:  # Short statement might be interrupted
                    speaker_data[speaker]["interruptions"] += 1

        # Create analytics objects
        analytics = []
        for speaker, data in speaker_data.items():
            analytics.append(SpeakerAnalytics(
                speaker_id=speaker,
                speaking_time=data["statements"] * 3,  # Rough estimate
                word_count=data["words"],
                interruptions=data["interruptions"],
                questions_asked=data["questions"],
                decisions_proposed=0,  # Would need more analysis
                sentiment_average=0.0,  # Would need sentiment analysis
                engagement_score=min(1.0, (data["questions"] + data["statements"]) / 20)
            ))

        return analytics

    async def _analyze_topics(self, transcript: List[Dict[str, Any]]) -> List[TopicAnalysis]:
        """Analyze topics discussed in the meeting"""
        if not transcript:
            return []

        # Combine transcript into chunks for topic analysis
        chunks = self._create_topic_chunks(transcript)
        topics = []

        for chunk in chunks:
            try:
                # Use GPT-4 to extract topic
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "Extract the main topic and key points from this meeting segment. Return as JSON."
                        },
                        {
                            "role": "user",
                            "content": f"Meeting segment:\n{chunk['text']}\n\nExtract: topic, key_points (list), decisions (list), action_items (list)"
                        }
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=200
                )

                result = json.loads(response.choices[0].message.content)

                topics.append(TopicAnalysis(
                    topic=result.get("topic", "General Discussion"),
                    duration=chunk["duration"],
                    speakers=chunk["speakers"],
                    sentiment=0.0,  # Would calculate separately
                    decisions=result.get("decisions", []),
                    action_items=result.get("action_items", []),
                    key_points=result.get("key_points", [])[:3]
                ))

            except Exception as e:
                logger.error(f"Topic analysis error: {e}")

        return topics

    def _create_topic_chunks(
        self,
        transcript: List[Dict[str, Any]],
        chunk_size: int = 10
    ) -> List[Dict[str, Any]]:
        """Create chunks of transcript for topic analysis"""
        chunks = []

        for i in range(0, len(transcript), chunk_size):
            chunk_transcript = transcript[i:i+chunk_size]

            if chunk_transcript:
                speakers = list(set(entry.get("speaker", "Unknown") for entry in chunk_transcript))
                text = "\n".join(f"{entry.get('speaker', 'Unknown')}: {entry.get('text', '')}"
                               for entry in chunk_transcript)

                chunks.append({
                    "text": text,
                    "speakers": speakers,
                    "duration": chunk_size * 0.5,  # Rough estimate
                    "start_index": i
                })

        return chunks

    async def _analyze_sentiment(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze meeting sentiment"""
        if not transcript:
            return {"overall": 0.0, "trend": "neutral"}

        sentiments = []

        # Analyze in batches
        for i in range(0, len(transcript), 5):
            batch = transcript[i:i+5]
            text = " ".join(entry.get("text", "") for entry in batch)

            if text:
                sentiment = await self._get_sentiment_score(text)
                sentiments.append(sentiment)
                self.sentiment_history.append((i, sentiment))

        overall = np.mean(sentiments) if sentiments else 0.0
        trend = self._calculate_sentiment_trend(sentiments)

        return {
            "overall": overall,
            "trend": trend,
            "history": sentiments,
            "positive_ratio": sum(1 for s in sentiments if s > 0.2) / len(sentiments) if sentiments else 0,
            "negative_ratio": sum(1 for s in sentiments if s < -0.2) / len(sentiments) if sentiments else 0
        }

    async def _get_sentiment_score(self, text: str) -> float:
        """Get sentiment score for text"""
        # Simple keyword-based sentiment (would use ML model in production)
        positive_words = ["good", "great", "excellent", "agree", "yes", "perfect", "wonderful", "happy"]
        negative_words = ["bad", "problem", "issue", "disagree", "no", "difficult", "concern", "worried"]

        text_lower = text.lower()
        positive_count = sum(word in text_lower for word in positive_words)
        negative_count = sum(word in text_lower for word in negative_words)

        if positive_count + negative_count == 0:
            return 0.0

        return (positive_count - negative_count) / (positive_count + negative_count)

    def _calculate_sentiment_trend(self, sentiments: List[float]) -> str:
        """Calculate sentiment trend"""
        if len(sentiments) < 2:
            return "stable"

        # Calculate trend using simple linear regression
        x = np.arange(len(sentiments))
        slope = np.polyfit(x, sentiments, 1)[0]

        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"

    async def _extract_insights(
        self,
        transcript: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> List[str]:
        """Extract key insights from the meeting"""
        insights = []

        # Participation insight
        if stats.get("unique_speakers", 0) > 5:
            insights.append("High participation with multiple contributors")
        elif stats.get("unique_speakers", 0) < 3:
            insights.append("Limited participation - consider engaging more team members")

        # Length insight
        if stats.get("duration_minutes", 0) > 60:
            insights.append("Long meeting - consider breaking into smaller sessions")

        # Productivity insight
        wpm = stats.get("words_per_minute", 0)
        if wpm > 150:
            insights.append("Fast-paced discussion with high information density")
        elif wpm < 50:
            insights.append("Slow-paced meeting - may benefit from more structure")

        return insights

    def _calculate_metrics(
        self,
        stats: Dict[str, Any],
        speaker_analytics: List[SpeakerAnalytics]
    ) -> MeetingMetrics:
        """Calculate meeting metrics"""
        # Participation balance (Gini coefficient)
        if speaker_analytics:
            word_counts = [s.word_count for s in speaker_analytics]
            participation_balance = 1 - self._calculate_gini(word_counts)
        else:
            participation_balance = 0.0

        # Engagement level
        total_questions = sum(s.questions_asked for s in speaker_analytics)
        engagement_level = min(1.0, total_questions / (stats.get("total_statements", 1) * 0.2))

        # Decision velocity (placeholder)
        decision_velocity = 0.1  # Would calculate from actual decisions

        # Topic coherence (placeholder)
        topic_coherence = 0.7  # Would calculate from topic transitions

        # Sentiment score (placeholder)
        sentiment_score = 0.0  # Would get from sentiment analysis

        # Productivity score (combination of factors)
        productivity_score = (
            participation_balance * 0.25 +
            engagement_level * 0.25 +
            decision_velocity * 0.25 +
            topic_coherence * 0.25
        )

        return MeetingMetrics(
            participation_balance=participation_balance,
            engagement_level=engagement_level,
            decision_velocity=decision_velocity,
            topic_coherence=topic_coherence,
            sentiment_score=sentiment_score,
            productivity_score=productivity_score
        )

    def _calculate_gini(self, values: List[float]) -> float:
        """Calculate Gini coefficient for inequality measurement"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        n = len(values)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

    def _identify_patterns(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify communication patterns"""
        patterns = {
            "dominant_speaker": None,
            "question_clusters": [],
            "decision_points": [],
            "topic_shifts": [],
            "engagement_drops": []
        }

        # Find dominant speaker
        speaker_counts = Counter(entry.get("speaker", "Unknown") for entry in transcript)
        if speaker_counts:
            dominant = speaker_counts.most_common(1)[0]
            if dominant[1] > len(transcript) * 0.4:
                patterns["dominant_speaker"] = dominant[0]

        # Find question clusters
        for i in range(len(transcript) - 2):
            window = transcript[i:i+3]
            questions = sum(1 for entry in window
                          if "?" in entry.get("text", ""))
            if questions >= 2:
                patterns["question_clusters"].append(i)

        return patterns

    def _determine_meeting_phase(self, transcript: List[Dict[str, Any]]) -> str:
        """Determine current meeting phase"""
        if not transcript:
            return "not_started"

        position = len(transcript)

        if position < 5:
            return "introduction"
        elif position < 15:
            return "warm_up"
        elif any("agenda" in entry.get("text", "").lower() for entry in transcript[-5:]):
            return "agenda_review"
        elif any("decision" in entry.get("text", "").lower() for entry in transcript[-5:]):
            return "decision_making"
        elif any("action" in entry.get("text", "").lower() for entry in transcript[-5:]):
            return "action_planning"
        elif any("next steps" in entry.get("text", "").lower() for entry in transcript[-5:]):
            return "wrap_up"
        else:
            return "discussion"

    async def _extract_action_items(self, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract action items from transcript"""
        action_items = []

        for entry in transcript:
            text = entry.get("text", "")

            # Check for action patterns
            for pattern in self.action_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Extract action item details
                    action_items.append({
                        "text": text,
                        "speaker": entry.get("speaker", "Unknown"),
                        "timestamp": entry.get("timestamp", ""),
                        "confidence": 0.8
                    })
                    break

        return action_items

    async def _extract_decisions(self, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract decisions from transcript"""
        decisions = []

        for entry in transcript:
            text = entry.get("text", "")

            # Check for decision patterns
            for pattern in self.decision_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    decisions.append({
                        "decision": text,
                        "speaker": entry.get("speaker", "Unknown"),
                        "timestamp": entry.get("timestamp", ""),
                        "confidence": 0.7
                    })
                    break

        return decisions

    def _identify_key_moments(self, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key moments in the meeting"""
        key_moments = []

        for i, entry in enumerate(transcript):
            text = entry.get("text", "").lower()

            # Decision moment
            if any(word in text for word in ["decided", "agreed", "confirmed"]):
                key_moments.append({
                    "type": "decision",
                    "index": i,
                    "text": entry.get("text", ""),
                    "speaker": entry.get("speaker", "Unknown")
                })

            # Question moment
            elif "?" in text and len(text) > 20:
                key_moments.append({
                    "type": "important_question",
                    "index": i,
                    "text": entry.get("text", ""),
                    "speaker": entry.get("speaker", "Unknown")
                })

            # Action item moment
            elif any(word in text for word in ["will", "action item", "responsible"]):
                key_moments.append({
                    "type": "action_item",
                    "index": i,
                    "text": entry.get("text", ""),
                    "speaker": entry.get("speaker", "Unknown")
                })

        return key_moments

    def _estimate_duration(self, transcript: List[Dict[str, Any]]) -> float:
        """Estimate meeting duration in minutes"""
        # Rough estimate based on average speaking rate
        total_words = sum(len(entry.get("text", "").split()) for entry in transcript)
        return total_words / 150  # Assuming 150 words per minute

    async def generate_summary(
        self,
        transcript: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        action_items: List[Dict[str, Any]],
        my_contributions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive meeting summary"""
        try:
            # Prepare transcript text
            transcript_text = "\n".join(
                f"{entry.get('speaker', 'Unknown')}: {entry.get('text', '')}"
                for entry in transcript[-50:]  # Last 50 entries for context
            )

            # Generate summary using GPT-4
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a meeting assistant. Create a concise, professional meeting summary."
                    },
                    {
                        "role": "user",
                        "content": f"""Create a meeting summary with these sections:
1. Overview (2-3 sentences)
2. Key Discussion Points (3-5 bullets)
3. Decisions Made
4. Action Items with Owners
5. Next Steps

Transcript excerpt:
{transcript_text}

Decisions: {json.dumps(decisions[:5])}
Action Items: {json.dumps(action_items[:5])}
"""
                    }
                ],
                max_tokens=500
            )

            summary_text = response.choices[0].message.content

            return {
                "summary": summary_text,
                "statistics": {
                    "duration": self._estimate_duration(transcript),
                    "participants": len(set(e.get("speaker", "Unknown") for e in transcript)),
                    "total_statements": len(transcript),
                    "decisions_made": len(decisions),
                    "action_items": len(action_items),
                    "ai_contributions": len(my_contributions)
                },
                "decisions": decisions[:10],
                "action_items": action_items[:10],
                "ai_participation": {
                    "contributions": len(my_contributions),
                    "contribution_rate": len(my_contributions) / len(transcript) if transcript else 0
                },
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {
                "summary": "Failed to generate summary",
                "error": str(e)
            }