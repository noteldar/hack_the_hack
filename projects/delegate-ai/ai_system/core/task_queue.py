"""
Task Queue System for Agent Task Management
"""

import asyncio
import heapq
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..config import AgentPriority
from .base_agent import AgentTask

@dataclass(order=True)
class PrioritizedTask:
    """Task wrapper with priority for queue ordering"""
    priority: int
    task: AgentTask = field(compare=False)
    enqueued_at: datetime = field(default_factory=datetime.now, compare=False)

class TaskQueue:
    """
    Priority-based task queue for managing agent tasks
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.logger = logging.getLogger("delegate.queue")

        # Priority queue (min-heap)
        self._queue: List[PrioritizedTask] = []

        # Task lookup
        self._task_map: Dict[str, AgentTask] = {}

        # Queue statistics
        self.stats = {
            "total_enqueued": 0,
            "total_dequeued": 0,
            "total_dropped": 0,
            "avg_wait_time": 0.0
        }

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def enqueue(self, task: AgentTask, priority: AgentPriority = None) -> bool:
        """Add a task to the queue"""
        async with self._lock:
            # Check if queue is full
            if len(self._queue) >= self.max_size:
                self.logger.warning(f"Queue full, dropping task {task.task_id}")
                self.stats["total_dropped"] += 1
                return False

            # Use task priority or override
            task_priority = priority or task.priority

            # Create prioritized task
            prioritized = PrioritizedTask(
                priority=task_priority.value,
                task=task
            )

            # Add to queue
            heapq.heappush(self._queue, prioritized)
            self._task_map[task.task_id] = task

            # Update stats
            self.stats["total_enqueued"] += 1

            self.logger.debug(f"Enqueued task {task.task_id} with priority {task_priority}")
            return True

    async def dequeue(self) -> Optional[AgentTask]:
        """Remove and return the highest priority task"""
        async with self._lock:
            if not self._queue:
                return None

            # Get highest priority task
            prioritized = heapq.heappop(self._queue)
            task = prioritized.task

            # Remove from map
            if task.task_id in self._task_map:
                del self._task_map[task.task_id]

            # Update wait time statistics
            wait_time = (datetime.now() - prioritized.enqueued_at).total_seconds()
            self._update_avg_wait_time(wait_time)

            # Update stats
            self.stats["total_dequeued"] += 1

            self.logger.debug(f"Dequeued task {task.task_id} (waited {wait_time:.2f}s)")
            return task

    async def peek(self) -> Optional[AgentTask]:
        """Look at the highest priority task without removing it"""
        async with self._lock:
            if not self._queue:
                return None
            return self._queue[0].task

    async def remove_task(self, task_id: str) -> bool:
        """Remove a specific task from the queue"""
        async with self._lock:
            if task_id not in self._task_map:
                return False

            # Remove from map
            task = self._task_map[task_id]
            del self._task_map[task_id]

            # Rebuild queue without this task
            self._queue = [p for p in self._queue if p.task.task_id != task_id]
            heapq.heapify(self._queue)

            self.logger.info(f"Removed task {task_id} from queue")
            return True

    async def reprioritize_task(self, task_id: str, new_priority: AgentPriority) -> bool:
        """Change the priority of a task in the queue"""
        async with self._lock:
            if task_id not in self._task_map:
                return False

            # Find and update the task
            for i, prioritized in enumerate(self._queue):
                if prioritized.task.task_id == task_id:
                    # Update priority
                    prioritized.priority = new_priority.value
                    prioritized.task.priority = new_priority

                    # Re-heapify
                    heapq.heapify(self._queue)

                    self.logger.info(f"Reprioritized task {task_id} to {new_priority}")
                    return True

            return False

    async def get_tasks_by_priority(self, priority: AgentPriority) -> List[AgentTask]:
        """Get all tasks with a specific priority"""
        async with self._lock:
            return [
                p.task for p in self._queue
                if p.priority == priority.value
            ]

    async def get_pending_dependencies(self, task_id: str) -> List[str]:
        """Get list of task IDs that the given task depends on"""
        async with self._lock:
            if task_id in self._task_map:
                return self._task_map[task_id].dependencies
            return []

    def size(self) -> int:
        """Get current queue size"""
        return len(self._queue)

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self._queue) == 0

    def is_full(self) -> bool:
        """Check if queue is full"""
        return len(self._queue) >= self.max_size

    def _update_avg_wait_time(self, wait_time: float):
        """Update average wait time statistic"""
        total_processed = self.stats["total_dequeued"]
        if total_processed == 0:
            self.stats["avg_wait_time"] = wait_time
        else:
            self.stats["avg_wait_time"] = (
                (self.stats["avg_wait_time"] * (total_processed - 1) + wait_time) /
                total_processed
            )

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        priority_distribution = {}
        for prioritized in self._queue:
            priority_name = AgentPriority(prioritized.priority).name
            priority_distribution[priority_name] = priority_distribution.get(priority_name, 0) + 1

        return {
            **self.stats,
            "current_size": self.size(),
            "max_size": self.max_size,
            "priority_distribution": priority_distribution,
            "oldest_task_wait": (
                (datetime.now() - min(self._queue, key=lambda x: x.enqueued_at).enqueued_at).total_seconds()
                if self._queue else 0
            )
        }

    async def clear(self):
        """Clear all tasks from the queue"""
        async with self._lock:
            self._queue.clear()
            self._task_map.clear()
            self.logger.info("Queue cleared")

    async def get_all_tasks(self) -> List[Tuple[AgentTask, AgentPriority, float]]:
        """Get all tasks with their priorities and wait times"""
        async with self._lock:
            tasks = []
            for prioritized in self._queue:
                wait_time = (datetime.now() - prioritized.enqueued_at).total_seconds()
                tasks.append((
                    prioritized.task,
                    AgentPriority(prioritized.priority),
                    wait_time
                ))
            return sorted(tasks, key=lambda x: x[1].value)  # Sort by priority