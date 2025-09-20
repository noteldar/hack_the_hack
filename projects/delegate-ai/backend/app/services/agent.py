from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status

from app.models.agent import Agent, AgentActivity, AgentType, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate, AgentActivityCreate


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(self, user_id: int, agent_create: AgentCreate) -> Agent:
        """Create a new AI agent"""
        agent = Agent(
            name=agent_create.name,
            agent_type=agent_create.agent_type,
            description=agent_create.description,
            config=agent_create.config,
            is_enabled=agent_create.is_enabled,
            user_id=user_id,
            status=AgentStatus.IDLE
        )

        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agent_by_id(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_user_agents(
        self,
        user_id: int,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentStatus] = None,
        is_enabled: Optional[bool] = None
    ) -> List[Agent]:
        """Get user's agents with filtering"""
        query = select(Agent).where(Agent.user_id == user_id)

        if agent_type:
            query = query.where(Agent.agent_type == agent_type)
        if status:
            query = query.where(Agent.status == status)
        if is_enabled is not None:
            query = query.where(Agent.is_enabled == is_enabled)

        query = query.order_by(Agent.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_agent(self, agent_id: int, agent_update: AgentUpdate) -> Agent:
        """Update an agent"""
        # Get existing agent
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        # Update fields
        update_data = agent_update.model_dump(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(Agent)
                .where(Agent.id == agent_id)
                .values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(agent)

        return agent

    async def delete_agent(self, agent_id: int) -> None:
        """Delete an agent"""
        await self.db.execute(delete(Agent).where(Agent.id == agent_id))
        await self.db.commit()

    async def get_agent_activities(
        self,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentActivity]:
        """Get agent activities"""
        query = select(AgentActivity).where(AgentActivity.agent_id == agent_id)
        query = query.offset(skip).limit(limit).order_by(AgentActivity.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def log_activity(
        self,
        agent_id: int,
        activity_create: AgentActivityCreate
    ) -> AgentActivity:
        """Log agent activity"""
        activity = AgentActivity(
            agent_id=agent_id,
            activity_type=activity_create.activity_type,
            description=activity_create.description,
            details=activity_create.details,
            execution_time=activity_create.execution_time,
            success=activity_create.success,
            error_message=activity_create.error_message,
            related_email_id=activity_create.related_email_id,
            related_task_id=activity_create.related_task_id,
            related_meeting_id=activity_create.related_meeting_id
        )

        self.db.add(activity)

        # Update agent's last_active timestamp
        await self.db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(last_active=datetime.utcnow())
        )

        await self.db.commit()
        await self.db.refresh(activity)
        return activity