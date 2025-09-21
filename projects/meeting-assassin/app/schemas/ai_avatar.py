"""
AI Avatar schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class PersonalityType(str, Enum):
    PROFESSIONAL = "professional"
    ASSERTIVE = "assertive"
    COLLABORATIVE = "collaborative"
    PROTECTIVE = "protective"
    EFFICIENT = "efficient"


class DecisionScenario(str, Enum):
    MEETING_INVITATION = "meeting_invitation"
    SCHEDULING_CONFLICT = "scheduling_conflict"
    RESCHEDULE_REQUEST = "reschedule_request"
    FOCUS_TIME_PROTECTION = "focus_time_protection"
    OPTIMIZATION_DECISION = "optimization_decision"


class PersonalityUpdate(BaseModel):
    personality_type: PersonalityType
    decision_autonomy: float  # 0.0 to 1.0
    auto_decline_conflicts: bool = False
    auto_suggest_reschedule: bool = True
    traits: Optional[Dict[str, Any]] = {}


class DecisionRequest(BaseModel):
    scenario: DecisionScenario
    context: Dict[str, Any]
    meeting_id: Optional[int] = None


class DecisionResponse(BaseModel):
    decision_type: str
    confidence: float
    reasoning: str
    suggested_actions: List[str]
    timestamp: datetime


class PersonalityAnalysis(BaseModel):
    personality_type: str
    traits: Dict[str, float]
    decision_patterns: Dict[str, Any]
    effectiveness_score: float


class AvatarStats(BaseModel):
    total_decisions: int
    decisions_accepted: int
    decisions_rejected: int
    accuracy_rate: float
    avg_confidence: float
    time_saved_hours: float
    personality_type: str