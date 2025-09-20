"""
Base Agent Class - Foundation for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass, field
import json
import traceback

from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool

from ..config import AgentConfig, AgentStatus, AgentPriority

@dataclass
class TaskResult:
    """Result of an agent task execution"""
    task_id: str
    agent_name: str
    status: str
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentTask:
    """Task definition for agent execution"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    priority: AgentPriority = AgentPriority.MEDIUM
    requester: Optional[str] = None
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class BaseAgent(ABC):
    """
    Base class for all AI agents in the Delegate.ai system.
    Provides core functionality for autonomous operation.
    """

    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[BaseTool]] = None,
        memory_window: int = 10
    ):
        self.config = config
        self.logger = logging.getLogger(f"delegate.{config.name}")
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None

        # Initialize LLM
        self.llm = llm or ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            return_messages=True,
            memory_key="chat_history"
        )

        # Initialize tools
        self.tools = tools or []
        self._register_default_tools()

        # Task tracking
        self.completed_tasks: List[TaskResult] = []
        self.failed_tasks: List[TaskResult] = []

        # Learning and adaptation
        self.user_preferences: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "total_tasks": 0
        }

        # Callback handlers
        self.callbacks: Dict[str, List[Callable]] = {
            "on_task_start": [],
            "on_task_complete": [],
            "on_task_error": [],
            "on_status_change": []
        }

        # Initialize agent executor
        self._initialize_executor()

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass

    @abstractmethod
    def _get_specialized_tools(self) -> List[BaseTool]:
        """Return specialized tools for this agent type"""
        pass

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute a specific task - must be implemented by subclasses"""
        pass

    def _register_default_tools(self):
        """Register default tools available to all agents"""
        specialized_tools = self._get_specialized_tools()
        if specialized_tools:
            self.tools.extend(specialized_tools)

    def _initialize_executor(self):
        """Initialize the LangChain agent executor"""
        from langchain.agents import create_openai_functions_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Create executor
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    async def run(self, task: AgentTask) -> TaskResult:
        """
        Main execution method for running agent tasks autonomously
        """
        start_time = datetime.now()
        self.current_task = task
        self._set_status(AgentStatus.WORKING)

        # Trigger callbacks
        await self._trigger_callbacks("on_task_start", task)

        try:
            # Log task start
            self.logger.info(f"Starting task: {task.task_id} - {task.description}")

            # Execute the task
            result = await self.execute_task(task)

            # Update metrics
            self._update_metrics(True, (datetime.now() - start_time).total_seconds())

            # Store result
            self.completed_tasks.append(result)

            # Trigger callbacks
            await self._trigger_callbacks("on_task_complete", result)

            return result

        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

            # Create error result
            result = TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="error",
                result=None,
                error=error_msg,
                execution_time=(datetime.now() - start_time).total_seconds()
            )

            # Update metrics
            self._update_metrics(False, (datetime.now() - start_time).total_seconds())

            # Store failed task
            self.failed_tasks.append(result)

            # Trigger callbacks
            await self._trigger_callbacks("on_task_error", result)

            return result

        finally:
            self.current_task = None
            self._set_status(AgentStatus.IDLE)

    def _set_status(self, status: AgentStatus):
        """Update agent status"""
        old_status = self.status
        self.status = status
        self.logger.debug(f"Status changed: {old_status} -> {status}")

        # Trigger status change callbacks
        asyncio.create_task(
            self._trigger_callbacks("on_status_change", old_status, status)
        )

    def _update_metrics(self, success: bool, execution_time: float):
        """Update performance metrics"""
        total = self.performance_metrics["total_tasks"]
        success_count = self.performance_metrics["success_rate"] * total

        if success:
            success_count += 1

        total += 1

        # Update metrics
        self.performance_metrics["total_tasks"] = total
        self.performance_metrics["success_rate"] = success_count / total
        self.performance_metrics["avg_execution_time"] = (
            (self.performance_metrics["avg_execution_time"] * (total - 1) + execution_time) / total
        )

    async def _trigger_callbacks(self, event: str, *args):
        """Trigger registered callbacks for an event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(self, *args)
                    else:
                        callback(self, *args)
                except Exception as e:
                    self.logger.error(f"Callback error for {event}: {e}")

    def register_callback(self, event: str, callback: Callable):
        """Register a callback for an event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def learn_from_feedback(self, task_id: str, feedback: Dict[str, Any]):
        """Learn from user feedback to improve future performance"""
        self.logger.info(f"Learning from feedback for task {task_id}")

        # Update user preferences based on feedback
        if "preferences" in feedback:
            self.user_preferences.update(feedback["preferences"])

        # Store feedback for future analysis
        for task in self.completed_tasks + self.failed_tasks:
            if task.task_id == task_id:
                task.metadata["user_feedback"] = feedback
                break

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report for this agent"""
        return {
            "agent_name": self.config.name,
            "status": self.status.value,
            "metrics": self.performance_metrics,
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "user_preferences": self.user_preferences
        }

    async def collaborate_with(self, other_agent: 'BaseAgent', message: Dict[str, Any]):
        """Enable inter-agent collaboration"""
        self.logger.info(f"Collaborating with {other_agent.config.name}")

        # Store collaboration in memory
        self.memory.chat_memory.add_message(
            AIMessage(content=f"Collaboration request to {other_agent.config.name}: {json.dumps(message)}")
        )

        # The actual collaboration logic will be handled by the InterAgentCommunicator
        return {
            "from": self.config.name,
            "to": other_agent.config.name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

    def reset(self):
        """Reset agent state"""
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.memory.clear()
        self.logger.info(f"Agent {self.config.name} has been reset")