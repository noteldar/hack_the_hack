"""
Calendar optimization endpoints using genetic algorithms
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.user import User
from app.schemas.optimization import (
    OptimizationRequest, OptimizationResponse,
    OptimizationResult, GeneticAlgorithmParams
)
from app.services.auth import AuthService
from app.services.optimization import OptimizationService
from app.core.websocket import WebSocketManager

router = APIRouter()
auth_service = AuthService()
optimization_service = OptimizationService()
websocket_manager = WebSocketManager()


@router.post("/schedule", response_model=OptimizationResponse)
async def optimize_schedule(
    optimization_request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Optimize calendar schedule using genetic algorithm"""
    try:
        # Start optimization process in background
        optimization_id = f"opt_{current_user.id}_{datetime.utcnow().timestamp()}"

        background_tasks.add_task(
            optimization_service.optimize_calendar,
            current_user.id,
            optimization_request,
            optimization_id
        )

        return OptimizationResponse(
            optimization_id=optimization_id,
            status="started",
            message="Calendar optimization initiated",
            estimated_completion_time=datetime.utcnow() + timedelta(minutes=5)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start optimization: {str(e)}"
        )


@router.get("/schedule/{optimization_id}")
async def get_optimization_result(
    optimization_id: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get optimization result by ID"""
    try:
        result = await optimization_service.get_optimization_result(optimization_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Optimization result not found"
            )

        # Ensure user owns this optimization
        if result.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get optimization result: {str(e)}"
        )


@router.get("/suggestions/reschedule")
async def get_reschedule_suggestions(
    days_ahead: int = 7,
    max_suggestions: int = 10,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered reschedule suggestions"""
    try:
        suggestions = await optimization_service.get_reschedule_suggestions(
            current_user.id,
            days_ahead,
            max_suggestions,
            db
        )

        return {
            "suggestions": suggestions,
            "count": len(suggestions),
            "period_days": days_ahead
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.post("/focus-time/optimize")
async def optimize_focus_time(
    background_tasks: BackgroundTasks,
    target_hours: float = 4.0,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Optimize calendar for maximum focus time"""
    try:
        optimization_id = f"focus_{current_user.id}_{datetime.utcnow().timestamp()}"

        background_tasks.add_task(
            optimization_service.optimize_focus_time,
            current_user.id,
            target_hours,
            optimization_id
        )

        return {
            "optimization_id": optimization_id,
            "status": "started",
            "target_focus_hours": target_hours,
            "message": "Focus time optimization initiated"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize focus time: {str(e)}"
        )


@router.get("/conflicts/resolve")
async def resolve_conflicts(
    background_tasks: BackgroundTasks,
    auto_apply: bool = False,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Resolve scheduling conflicts automatically"""
    try:
        resolution_id = f"resolve_{current_user.id}_{datetime.utcnow().timestamp()}"

        background_tasks.add_task(
            optimization_service.resolve_conflicts,
            current_user.id,
            auto_apply,
            resolution_id
        )

        return {
            "resolution_id": resolution_id,
            "status": "started",
            "auto_apply": auto_apply,
            "message": "Conflict resolution initiated"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflicts: {str(e)}"
        )


@router.get("/analytics/fitness")
async def get_fitness_analytics(
    days: int = 30,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get calendar fitness analytics"""
    try:
        analytics = await optimization_service.get_fitness_analytics(
            current_user.id,
            days,
            db
        )

        return analytics

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fitness analytics: {str(e)}"
        )


@router.post("/genetic/params")
async def update_genetic_params(
    params: GeneticAlgorithmParams,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update genetic algorithm parameters for optimization"""
    try:
        # Validate parameters
        if not (10 <= params.population_size <= 200):
            raise ValueError("Population size must be between 10 and 200")

        if not (0.01 <= params.mutation_rate <= 0.5):
            raise ValueError("Mutation rate must be between 0.01 and 0.5")

        if not (0.3 <= params.crossover_rate <= 1.0):
            raise ValueError("Crossover rate must be between 0.3 and 1.0")

        # Store parameters for user
        await optimization_service.update_user_ga_params(current_user.id, params)

        return {
            "message": "Genetic algorithm parameters updated",
            "parameters": params.dict()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update parameters: {str(e)}"
        )


@router.get("/batch/status")
async def get_batch_optimization_status(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get status of all running optimizations for user"""
    try:
        status = await optimization_service.get_user_optimization_status(current_user.id)
        return status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get optimization status: {str(e)}"
        )


@router.post("/test/algorithm")
async def test_genetic_algorithm(
    test_params: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Test genetic algorithm with sample data"""
    try:
        test_result = await optimization_service.test_algorithm(
            current_user.id,
            test_params or {}
        )

        return {
            "test_completed": True,
            "result": test_result,
            "message": "Algorithm test completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Algorithm test failed: {str(e)}"
        )