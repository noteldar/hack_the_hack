from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, user_id: int, task_create: TaskCreate) -> Task:
        """Create a new task"""
        task = Task(
            title=task_create.title,
            description=task_create.description,
            priority=task_create.priority,
            due_date=task_create.due_date,
            estimated_duration=task_create.estimated_duration,
            tags=task_create.tags,
            notes=task_create.notes,
            user_id=user_id,
            meeting_id=task_create.meeting_id,
            email_id=task_create.email_id,
            status=TaskStatus.TODO
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """Get user's tasks with filtering"""
        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)

        query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        """Update a task"""
        # Get existing task
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(task)

        return task

    async def complete_task(self, task_id: int) -> Task:
        """Mark task as completed"""
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        await self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(
                status=TaskStatus.COMPLETED,
                completed_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_id: int) -> None:
        """Delete a task"""
        await self.db.execute(delete(Task).where(Task.id == task_id))
        await self.db.commit()