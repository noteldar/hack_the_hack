"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, calendar, meetings, users, ai_avatar, optimization, ai_intelligence

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(ai_avatar.router, prefix="/ai", tags=["AI Avatar"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["Calendar Optimization"])
api_router.include_router(ai_intelligence.router, prefix="/ai-intelligence", tags=["AI Intelligence"])