from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, calendar, emails, tasks, meetings, agents

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])