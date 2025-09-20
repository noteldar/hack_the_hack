"""
Configuration for the AI System
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class AgentPriority(Enum):
    """Priority levels for agent tasks"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class AgentStatus(Enum):
    """Status of agent execution"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class AgentConfig:
    """Base configuration for AI agents"""
    name: str
    description: str
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000
    max_retries: int = 3
    timeout: int = 60
    priority: AgentPriority = AgentPriority.MEDIUM
    autonomous: bool = True
    learning_enabled: bool = True

@dataclass
class SystemConfig:
    """System-wide configuration"""
    # API Keys (should be in environment variables)
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    serper_api_key: str = field(default_factory=lambda: os.getenv("SERPER_API_KEY", ""))

    # System Settings
    max_concurrent_agents: int = 5
    agent_communication_timeout: int = 30
    memory_persistence_enabled: bool = True
    memory_db_path: str = "./data/agent_memory.db"

    # Execution Settings
    proactive_mode: bool = True
    background_execution_interval: int = 300  # seconds
    task_queue_max_size: int = 100
    enable_failure_recovery: bool = True

    # Logging and Monitoring
    log_level: str = "INFO"
    enable_telemetry: bool = True
    performance_tracking: bool = True

    # Integration Settings
    calendar_sync_enabled: bool = True
    email_sync_enabled: bool = True
    slack_integration: bool = False
    teams_integration: bool = False

    # Learning and Adaptation
    user_preference_learning: bool = True
    context_window_size: int = 10
    feedback_collection: bool = True

# Agent-specific configurations
AGENT_CONFIGS = {
    "meeting_prep": AgentConfig(
        name="MeetingPrepAgent",
        description="Researches attendees and prepares meeting materials",
        temperature=0.6,
        priority=AgentPriority.HIGH,
        autonomous=True
    ),
    "task_orchestrator": AgentConfig(
        name="TaskOrchestratorAgent",
        description="Orchestrates task delegation and project management",
        temperature=0.5,
        priority=AgentPriority.CRITICAL,
        max_tokens=3000
    ),
    "communication": AgentConfig(
        name="CommunicationAgent",
        description="Manages email and communication workflows",
        temperature=0.7,
        priority=AgentPriority.HIGH
    ),
    "research": AgentConfig(
        name="ResearchAgent",
        description="Conducts background research and intelligence gathering",
        temperature=0.8,
        priority=AgentPriority.MEDIUM,
        max_tokens=4000
    ),
    "schedule_optimizer": AgentConfig(
        name="ScheduleOptimizer",
        description="Optimizes calendar and scheduling",
        temperature=0.4,
        priority=AgentPriority.MEDIUM
    )
}

# Default system configuration
DEFAULT_CONFIG = SystemConfig()