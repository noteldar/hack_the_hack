"""
Agent Orchestrator - Central coordination system for multi-agent collaboration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timedelta
import json
from collections import defaultdict
import uuid

from .base_agent import BaseAgent, AgentTask, TaskResult
from .memory import AgentMemoryManager
from .communication import InterAgentCommunicator
from .task_queue import TaskQueue
from .execution_engine import ExecutionEngine
from ..config import SystemConfig, AgentStatus, AgentPriority

class AgentOrchestrator:
    """
    Central orchestrator for managing multiple AI agents.
    Coordinates autonomous execution, inter-agent communication, and task delegation.
    """

    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.logger = logging.getLogger("delegate.orchestrator")

        # Agent registry
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, Type[BaseAgent]] = {}

        # Core components
        self.memory_manager = AgentMemoryManager(self.config.memory_db_path)
        self.communicator = InterAgentCommunicator()
        self.task_queue = TaskQueue(max_size=self.config.task_queue_max_size)
        self.execution_engine = ExecutionEngine(
            max_concurrent=self.config.max_concurrent_agents
        )

        # State tracking
        self.running = False
        self.background_tasks: List[asyncio.Task] = []
        self.task_history: Dict[str, TaskResult] = {}
        self.agent_workloads: Dict[str, int] = defaultdict(int)

        # Performance monitoring
        self.metrics = {
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "avg_task_completion_time": 0.0,
            "agent_utilization": {},
            "task_distribution": defaultdict(int)
        }

        # Task dependencies and workflow
        self.task_dependencies: Dict[str, List[str]] = {}
        self.workflow_templates: Dict[str, List[Dict]] = {}

        # Initialize proactive execution if enabled
        if self.config.proactive_mode:
            self._initialize_proactive_execution()

    def register_agent(self, agent_class: Type[BaseAgent], agent_id: str, **kwargs):
        """Register a new agent with the orchestrator"""
        try:
            # Create agent instance
            agent = agent_class(**kwargs)

            # Store in registry
            self.agents[agent_id] = agent
            self.agent_types[agent_class.__name__] = agent_class

            # Register callbacks
            agent.register_callback("on_task_complete", self._on_agent_task_complete)
            agent.register_callback("on_task_error", self._on_agent_task_error)

            # Initialize agent memory
            self.memory_manager.initialize_agent_memory(agent_id)

            # Register with communicator
            self.communicator.register_agent(agent_id, agent)

            self.logger.info(f"Registered agent: {agent_id} ({agent_class.__name__})")

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_id}: {e}")
            raise

    async def submit_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        priority: AgentPriority = AgentPriority.MEDIUM,
        agent_id: Optional[str] = None,
        dependencies: List[str] = None
    ) -> str:
        """Submit a new task to the orchestrator"""
        # Generate task ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        # Create task
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            parameters=parameters,
            priority=priority,
            dependencies=dependencies or []
        )

        # Store dependencies
        if dependencies:
            self.task_dependencies[task_id] = dependencies

        # Add to queue
        await self.task_queue.enqueue(task, priority)

        self.logger.info(f"Task submitted: {task_id} - {description}")

        # If a specific agent is requested, assign immediately
        if agent_id and agent_id in self.agents:
            await self._assign_task_to_agent(task, agent_id)
        else:
            # Let the orchestrator decide
            await self._schedule_task(task)

        return task_id

    async def _schedule_task(self, task: AgentTask):
        """Intelligently schedule a task to the most appropriate agent"""
        # Check dependencies
        if task.task_id in self.task_dependencies:
            if not await self._check_dependencies(task.task_id):
                # Re-queue the task
                await asyncio.sleep(5)
                await self.task_queue.enqueue(task, task.priority)
                return

        # Find the best agent for this task
        best_agent = await self._select_best_agent(task)

        if best_agent:
            await self._assign_task_to_agent(task, best_agent)
        else:
            # No suitable agent available, re-queue
            self.logger.warning(f"No suitable agent for task {task.task_id}, re-queuing")
            await asyncio.sleep(10)
            await self.task_queue.enqueue(task, task.priority)

    async def _select_best_agent(self, task: AgentTask) -> Optional[str]:
        """Select the best agent for a given task based on capability and availability"""
        suitable_agents = []

        for agent_id, agent in self.agents.items():
            # Check if agent is available
            if agent.status != AgentStatus.IDLE:
                continue

            # Check agent workload
            if self.agent_workloads[agent_id] >= 3:  # Max 3 concurrent tasks per agent
                continue

            # Check if agent can handle this task type
            if self._agent_can_handle_task(agent, task):
                suitable_agents.append((agent_id, agent))

        if not suitable_agents:
            return None

        # Sort by workload (ascending) and priority match
        suitable_agents.sort(key=lambda x: (
            self.agent_workloads[x[0]],
            abs(x[1].config.priority.value - task.priority.value)
        ))

        return suitable_agents[0][0]

    def _agent_can_handle_task(self, agent: BaseAgent, task: AgentTask) -> bool:
        """Determine if an agent can handle a specific task type"""
        # This is a simplified version - in production, you'd have more sophisticated matching
        task_type_mapping = {
            "meeting_prep": ["MeetingPrepAgent"],
            "task_management": ["TaskOrchestratorAgent"],
            "communication": ["CommunicationAgent"],
            "research": ["ResearchAgent"],
            "scheduling": ["ScheduleOptimizer"]
        }

        agent_type = agent.__class__.__name__
        return agent_type in task_type_mapping.get(task.task_type, [agent_type])

    async def _assign_task_to_agent(self, task: AgentTask, agent_id: str):
        """Assign a task to a specific agent"""
        if agent_id not in self.agents:
            self.logger.error(f"Agent {agent_id} not found")
            return

        agent = self.agents[agent_id]

        # Update workload
        self.agent_workloads[agent_id] += 1

        # Execute task asynchronously
        asyncio.create_task(self._execute_agent_task(agent, task))

    async def _execute_agent_task(self, agent: BaseAgent, task: AgentTask):
        """Execute a task with an agent and handle the result"""
        try:
            # Execute the task
            result = await agent.run(task)

            # Store result
            self.task_history[task.task_id] = result

            # Update metrics
            self._update_metrics(result)

            # Handle task completion
            await self._handle_task_completion(result)

        except Exception as e:
            self.logger.error(f"Failed to execute task {task.task_id}: {e}")

        finally:
            # Update workload
            self.agent_workloads[agent.config.name] = max(
                0, self.agent_workloads[agent.config.name] - 1
            )

    async def _handle_task_completion(self, result: TaskResult):
        """Handle post-task completion activities"""
        # Check for dependent tasks
        dependent_tasks = [
            task_id for task_id, deps in self.task_dependencies.items()
            if result.task_id in deps
        ]

        # Process dependent tasks
        for task_id in dependent_tasks:
            self.logger.info(f"Dependency satisfied for task {task_id}")
            # Re-evaluate the task for scheduling
            # This would fetch the task from queue and reschedule

        # Trigger any workflow continuation
        await self._continue_workflow(result)

    async def _continue_workflow(self, result: TaskResult):
        """Continue workflow execution based on task completion"""
        # Check if this task is part of a workflow
        for workflow_id, workflow in self.workflow_templates.items():
            # Implement workflow continuation logic
            pass

    async def _check_dependencies(self, task_id: str) -> bool:
        """Check if all dependencies for a task are satisfied"""
        if task_id not in self.task_dependencies:
            return True

        dependencies = self.task_dependencies[task_id]
        for dep_id in dependencies:
            if dep_id not in self.task_history:
                return False
            if self.task_history[dep_id].status != "success":
                return False

        return True

    def _initialize_proactive_execution(self):
        """Initialize proactive background execution"""
        self.logger.info("Initializing proactive execution mode")

        # Create background tasks for autonomous operation
        self.background_tasks.append(
            asyncio.create_task(self._proactive_task_generator())
        )
        self.background_tasks.append(
            asyncio.create_task(self._task_processor())
        )
        self.background_tasks.append(
            asyncio.create_task(self._health_monitor())
        )

    async def _proactive_task_generator(self):
        """Generate tasks proactively based on schedules and patterns"""
        while self.running:
            try:
                # Check for scheduled tasks
                current_time = datetime.now()

                # Example: Check for upcoming meetings and prepare
                if current_time.hour == 8:  # Morning preparation
                    await self._generate_morning_tasks()

                # Example: Regular research updates
                if current_time.minute == 0:  # Every hour
                    await self._generate_research_tasks()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in proactive task generation: {e}")
                await asyncio.sleep(60)

    async def _generate_morning_tasks(self):
        """Generate morning preparation tasks"""
        tasks = [
            {
                "type": "meeting_prep",
                "description": "Prepare for today's meetings",
                "parameters": {"date": datetime.now().date().isoformat()}
            },
            {
                "type": "scheduling",
                "description": "Optimize today's schedule",
                "parameters": {"optimization_type": "daily"}
            }
        ]

        for task in tasks:
            await self.submit_task(
                task_type=task["type"],
                description=task["description"],
                parameters=task["parameters"],
                priority=AgentPriority.HIGH
            )

    async def _generate_research_tasks(self):
        """Generate research and monitoring tasks"""
        # This would be more sophisticated in production
        pass

    async def _task_processor(self):
        """Process tasks from the queue continuously"""
        while self.running:
            try:
                # Get next task from queue
                task = await self.task_queue.dequeue()

                if task:
                    await self._schedule_task(task)

                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(5)

    async def _health_monitor(self):
        """Monitor system health and agent performance"""
        while self.running:
            try:
                # Check agent health
                for agent_id, agent in self.agents.items():
                    if agent.status == AgentStatus.ERROR:
                        self.logger.warning(f"Agent {agent_id} is in error state")
                        # Attempt recovery
                        agent.reset()

                # Log metrics
                if self.metrics["total_tasks_completed"] % 10 == 0:
                    self.logger.info(f"System metrics: {json.dumps(self.metrics, indent=2)}")

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(30)

    async def _on_agent_task_complete(self, agent: BaseAgent, result: TaskResult):
        """Callback for when an agent completes a task"""
        self.logger.info(f"Agent {agent.config.name} completed task {result.task_id}")

        # Update metrics
        self.metrics["total_tasks_completed"] += 1
        self.metrics["task_distribution"][agent.config.name] += 1

        # Store in memory
        await self.memory_manager.store_task_result(agent.config.name, result)

        # Check for follow-up tasks
        await self._generate_follow_up_tasks(result)

    async def _on_agent_task_error(self, agent: BaseAgent, result: TaskResult):
        """Callback for when an agent encounters an error"""
        self.logger.error(f"Agent {agent.config.name} failed task {result.task_id}: {result.error}")

        # Update metrics
        self.metrics["total_tasks_failed"] += 1

        # Attempt recovery if enabled
        if self.config.enable_failure_recovery:
            await self._attempt_task_recovery(result)

    async def _attempt_task_recovery(self, failed_result: TaskResult):
        """Attempt to recover from a failed task"""
        # Re-queue the task with a different agent or retry
        pass

    async def _generate_follow_up_tasks(self, result: TaskResult):
        """Generate follow-up tasks based on completed task results"""
        # This would analyze the result and create new tasks as needed
        pass

    def _update_metrics(self, result: TaskResult):
        """Update system metrics"""
        # Update average completion time
        total = self.metrics["total_tasks_completed"] + self.metrics["total_tasks_failed"]
        if total > 0:
            self.metrics["avg_task_completion_time"] = (
                (self.metrics["avg_task_completion_time"] * total + result.execution_time) /
                (total + 1)
            )

        # Update agent utilization
        self.metrics["agent_utilization"][result.agent_name] = (
            self.agent_workloads[result.agent_name] /
            self.config.max_concurrent_agents
        )

    async def start(self):
        """Start the orchestrator"""
        self.running = True
        self.logger.info("Agent Orchestrator started")

        # Start execution engine
        await self.execution_engine.start()

        # Start communication system
        await self.communicator.start()

        # Initialize proactive tasks if enabled
        if self.config.proactive_mode:
            self._initialize_proactive_execution()

    async def stop(self):
        """Stop the orchestrator"""
        self.running = False

        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Stop components
        await self.execution_engine.stop()
        await self.communicator.stop()

        # Save state
        await self.memory_manager.save_all()

        self.logger.info("Agent Orchestrator stopped")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "running": self.running,
            "agents": {
                agent_id: {
                    "status": agent.status.value,
                    "workload": self.agent_workloads[agent_id],
                    "performance": agent.get_performance_report()
                }
                for agent_id, agent in self.agents.items()
            },
            "queue_size": self.task_queue.size(),
            "metrics": self.metrics,
            "total_tasks_in_history": len(self.task_history)
        }