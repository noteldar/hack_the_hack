from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.deps import get_current_active_user
from app.models.user import User
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services.task import TaskService

router = APIRouter()


@router.post("/", response_model=Task)
async def create_task(
    task_create: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task"""
    task_service = TaskService(db)
    return await task_service.create_task(current_user.id, task_create)


@router.get("/", response_model=List[Task])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's tasks with filtering"""
    task_service = TaskService(db)
    return await task_service.get_user_tasks(
        current_user.id, skip=skip, limit=limit, status=status, priority=priority
    )


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific task"""
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a task"""
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await task_service.update_task(task_id, task_update)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a task"""
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await task_service.delete_task(task_id)
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark task as completed"""
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await task_service.complete_task(task_id)