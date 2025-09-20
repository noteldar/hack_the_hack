"""
Delegate.ai - Multi-Agent Orchestration System

A sophisticated AI system where specialized agents work autonomously
to manage productivity tasks as true "operators" rather than assistants.
"""

from .core.orchestrator import AgentOrchestrator
from .agents import (
    MeetingPrepAgent,
    TaskOrchestratorAgent,
    CommunicationAgent,
    ResearchAgent,
    ScheduleOptimizer
)
from .core.memory import AgentMemoryManager
from .core.communication import InterAgentCommunicator

__version__ = "1.0.0"

__all__ = [
    "AgentOrchestrator",
    "MeetingPrepAgent",
    "TaskOrchestratorAgent",
    "CommunicationAgent",
    "ResearchAgent",
    "ScheduleOptimizer",
    "AgentMemoryManager",
    "InterAgentCommunicator"
]