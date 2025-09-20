from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.deps import get_current_active_user
from app.models.user import User
from app.models.agent import AgentType, AgentStatus
from app.schemas.agent import Agent, AgentCreate, AgentUpdate, AgentActivity, AgentActivityCreate
from app.services.agent import AgentService

router = APIRouter()


@router.post("/", response_model=Agent)
async def create_agent(
    agent_create: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new AI agent"""
    agent_service = AgentService(db)
    return await agent_service.create_agent(current_user.id, agent_create)


@router.get("/", response_model=List[Agent])
async def get_agents(
    agent_type: Optional[AgentType] = None,
    status: Optional[AgentStatus] = None,
    is_enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's AI agents"""
    agent_service = AgentService(db)
    return await agent_service.get_user_agents(
        current_user.id, agent_type=agent_type, status=status, is_enabled=is_enabled
    )


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific AI agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent or agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.patch("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an AI agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent or agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return await agent_service.update_agent(agent_id, agent_update)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an AI agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent or agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    await agent_service.delete_agent(agent_id)
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/execute")
async def execute_agent_task(
    agent_id: int,
    task_description: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute a task with the AI agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent or agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    if not agent.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is disabled"
        )

    # This would trigger the agent execution
    # For now, return a placeholder response
    return {
        "message": "Agent task execution started",
        "agent_id": agent_id,
        "task_description": task_description
    }


@router.get("/{agent_id}/activities", response_model=List[AgentActivity])
async def get_agent_activities(
    agent_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get agent activity history"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent or agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return await agent_service.get_agent_activities(agent_id, skip=skip, limit=limit)


@router.post("/{agent_id}/activities", response_model=AgentActivity)
async def log_agent_activity(
    agent_id: int,
    activity_create: AgentActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Log agent activity (for internal use)"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent or agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return await agent_service.log_activity(agent_id, activity_create)