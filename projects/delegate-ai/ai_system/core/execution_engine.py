"""
Execution Engine for Concurrent Agent Task Processing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import traceback

from .base_agent import BaseAgent, AgentTask, TaskResult
from ..config import AgentStatus

class ExecutionEngine:
    """
    Manages concurrent execution of agent tasks with resource management
    """

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.logger = logging.getLogger("delegate.execution")

        # Execution tracking
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Execution statistics
        self.stats = {
            "total_executed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_execution_time": 0.0,
            "current_load": 0
        }

        # Resource tracking
        self.resource_usage: Dict[str, float] = defaultdict(float)

        # Execution hooks
        self.pre_execution_hooks: List[Callable] = []
        self.post_execution_hooks: List[Callable] = []

        # Running state
        self.running = False

    async def execute_task(
        self,
        agent: BaseAgent,
        task: AgentTask,
        timeout: Optional[int] = None
    ) -> TaskResult:
        """Execute a task with an agent"""
        async with self.semaphore:
            task_id = task.task_id
            start_time = datetime.now()

            # Update current load
            self.stats["current_load"] = len(self.running_tasks)

            try:
                # Run pre-execution hooks
                for hook in self.pre_execution_hooks:
                    await self._run_hook(hook, agent, task)

                self.logger.info(f"Starting execution: {task_id} with {agent.config.name}")

                # Create execution task
                if timeout:
                    execution = asyncio.wait_for(
                        agent.run(task),
                        timeout=timeout
                    )
                else:
                    execution = agent.run(task)

                # Track running task
                task_future = asyncio.create_task(execution)
                self.running_tasks[task_id] = task_future

                # Execute
                result = await task_future

                # Update statistics
                execution_time = (datetime.now() - start_time).total_seconds()
                self._update_stats(True, execution_time)

                # Run post-execution hooks
                for hook in self.post_execution_hooks:
                    await self._run_hook(hook, agent, result)

                self.logger.info(f"Completed execution: {task_id} in {execution_time:.2f}s")
                return result

            except asyncio.TimeoutError:
                error_msg = f"Task {task_id} timed out after {timeout} seconds"
                self.logger.error(error_msg)

                result = TaskResult(
                    task_id=task_id,
                    agent_name=agent.config.name,
                    status="timeout",
                    result=None,
                    error=error_msg,
                    execution_time=(datetime.now() - start_time).total_seconds()
                )

                self._update_stats(False, result.execution_time)
                return result

            except Exception as e:
                error_msg = f"Execution failed: {str(e)}\n{traceback.format_exc()}"
                self.logger.error(error_msg)

                result = TaskResult(
                    task_id=task_id,
                    agent_name=agent.config.name,
                    status="error",
                    result=None,
                    error=error_msg,
                    execution_time=(datetime.now() - start_time).total_seconds()
                )

                self._update_stats(False, result.execution_time)
                return result

            finally:
                # Clean up
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]

                self.stats["current_load"] = len(self.running_tasks)

    async def execute_batch(
        self,
        tasks: List[tuple[BaseAgent, AgentTask]],
        max_batch_concurrent: Optional[int] = None
    ) -> List[TaskResult]:
        """Execute multiple tasks concurrently"""
        batch_concurrent = max_batch_concurrent or self.max_concurrent

        # Create batch semaphore
        batch_semaphore = asyncio.Semaphore(batch_concurrent)

        async def execute_with_semaphore(agent, task):
            async with batch_semaphore:
                return await self.execute_task(agent, task)

        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[execute_with_semaphore(agent, task) for agent, task in tasks],
            return_exceptions=True
        )

        # Handle any exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent, task = tasks[i]
                processed_results.append(TaskResult(
                    task_id=task.task_id,
                    agent_name=agent.config.name,
                    status="error",
                    result=None,
                    error=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            self.logger.info(f"Cancelled task: {task_id}")
            return True
        return False

    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is currently running"""
        return task_id in self.running_tasks

    def get_running_tasks(self) -> List[str]:
        """Get list of currently running task IDs"""
        return list(self.running_tasks.keys())

    def add_pre_execution_hook(self, hook: Callable):
        """Add a hook to run before task execution"""
        self.pre_execution_hooks.append(hook)

    def add_post_execution_hook(self, hook: Callable):
        """Add a hook to run after task execution"""
        self.post_execution_hooks.append(hook)

    async def _run_hook(self, hook: Callable, *args):
        """Run a hook safely"""
        try:
            if asyncio.iscoroutinefunction(hook):
                await hook(*args)
            else:
                hook(*args)
        except Exception as e:
            self.logger.error(f"Hook execution failed: {e}")

    def _update_stats(self, success: bool, execution_time: float):
        """Update execution statistics"""
        self.stats["total_executed"] += 1

        if success:
            self.stats["successful_executions"] += 1
        else:
            self.stats["failed_executions"] += 1

        # Update average execution time
        total = self.stats["total_executed"]
        self.stats["avg_execution_time"] = (
            (self.stats["avg_execution_time"] * (total - 1) + execution_time) / total
        )

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        success_rate = (
            self.stats["successful_executions"] / self.stats["total_executed"]
            if self.stats["total_executed"] > 0 else 0
        )

        return {
            **self.stats,
            "success_rate": success_rate,
            "capacity_utilization": self.stats["current_load"] / self.max_concurrent
        }

    async def wait_for_capacity(self, required_slots: int = 1) -> bool:
        """Wait until there's enough execution capacity"""
        timeout = 60  # Maximum wait time in seconds
        start_time = datetime.now()

        while len(self.running_tasks) + required_slots > self.max_concurrent:
            if (datetime.now() - start_time).total_seconds() > timeout:
                return False

            await asyncio.sleep(1)

        return True

    async def start(self):
        """Start the execution engine"""
        self.running = True
        self.logger.info("Execution engine started")

    async def stop(self, cancel_running: bool = False):
        """Stop the execution engine"""
        self.running = False

        if cancel_running:
            # Cancel all running tasks
            for task_id in list(self.running_tasks.keys()):
                await self.cancel_task(task_id)

        # Wait for all tasks to complete
        if self.running_tasks:
            await asyncio.gather(
                *self.running_tasks.values(),
                return_exceptions=True
            )

        self.logger.info("Execution engine stopped")