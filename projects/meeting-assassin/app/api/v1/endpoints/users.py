"""
User management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse, UserPreferences
from app.services.auth import AuthService

router = APIRouter()
auth_service = AuthService()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    try:
        update_data = user_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(current_user, field, value)

        await db.commit()
        await db.refresh(current_user)

        return UserResponse.from_orm(current_user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get user preferences and settings"""
    return UserPreferences(
        timezone=current_user.timezone,
        work_hours_start=current_user.work_hours_start,
        work_hours_end=current_user.work_hours_end,
        preferred_meeting_duration=current_user.preferred_meeting_duration,
        avatar_personality=current_user.avatar_personality,
        ai_decision_autonomy=current_user.ai_decision_autonomy,
        auto_decline_conflicts=current_user.auto_decline_conflicts,
        auto_suggest_reschedule=current_user.auto_suggest_reschedule,
        focus_time_blocks=current_user.focus_time_blocks,
        focus_block_duration=current_user.focus_block_duration,
        break_duration=current_user.break_duration
    )


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    try:
        # Update preferences
        current_user.timezone = preferences.timezone
        current_user.work_hours_start = preferences.work_hours_start
        current_user.work_hours_end = preferences.work_hours_end
        current_user.preferred_meeting_duration = preferences.preferred_meeting_duration
        current_user.avatar_personality = preferences.avatar_personality
        current_user.ai_decision_autonomy = preferences.ai_decision_autonomy
        current_user.auto_decline_conflicts = preferences.auto_decline_conflicts
        current_user.auto_suggest_reschedule = preferences.auto_suggest_reschedule
        current_user.focus_time_blocks = preferences.focus_time_blocks
        current_user.focus_block_duration = preferences.focus_block_duration
        current_user.break_duration = preferences.break_duration

        await db.commit()
        await db.refresh(current_user)

        return preferences

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/me/avatar-config")
async def get_avatar_config(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get AI avatar configuration"""
    return current_user.get_avatar_config()


@router.delete("/me/account")
async def delete_user_account(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account (soft delete)"""
    try:
        # In production, implement soft delete or data retention
        # For now, just clear sensitive data
        current_user.access_token = None
        current_user.refresh_token = None
        current_user.google_id = None

        await db.commit()

        return {"message": "Account deletion initiated"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )