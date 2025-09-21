"""
API dependencies for MeetingAssassin
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import get_db
from app.models.user import User
from app.core.config import settings
from typing import Optional
import jwt
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""

    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""

    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user

    except jwt.PyJWTError:
        return None


def require_calendar_connected(user: User = Depends(get_current_user)) -> User:
    """Require that user has Google Calendar connected"""

    if not user.calendar_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar must be connected to use this feature"
        )

    return user


def require_admin_user(user: User = Depends(get_current_user)) -> User:
    """Require that user is an admin"""

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user


async def validate_calendar_permissions(
    user: User = Depends(require_calendar_connected),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate that user has necessary calendar permissions"""

    from app.services.oauth_service import oauth_service

    try:
        access_token = await oauth_service.get_valid_access_token(user, db)
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid calendar access token. Please reconnect your calendar."
            )

        # Check permissions
        permissions = await oauth_service.check_calendar_permissions(access_token)
        required_permissions = ["read_calendar", "write_calendar", "read_events", "write_events"]

        missing_permissions = [
            perm for perm in required_permissions
            if not permissions.get(perm, False)
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing calendar permissions: {', '.join(missing_permissions)}"
            )

        return user

    except Exception as e:
        logger.error(f"Calendar permission validation failed for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate calendar permissions"
        )


class RateLimitDependency:
    """Rate limiting dependency"""

    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.call_history = {}

    async def __call__(self, user: User = Depends(get_current_user)):
        import time

        current_time = time.time()
        user_id = user.id

        # Clean old entries
        if user_id in self.call_history:
            self.call_history[user_id] = [
                timestamp for timestamp in self.call_history[user_id]
                if current_time - timestamp < self.period
            ]
        else:
            self.call_history[user_id] = []

        # Check rate limit
        if len(self.call_history[user_id]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.calls} calls per {self.period} seconds"
            )

        # Add current call
        self.call_history[user_id].append(current_time)

        return user


# Rate limit instances
rate_limit_sync = RateLimitDependency(calls=5, period=300)  # 5 syncs per 5 minutes
rate_limit_events = RateLimitDependency(calls=100, period=3600)  # 100 event operations per hour
rate_limit_analytics = RateLimitDependency(calls=20, period=3600)  # 20 analytics calls per hour


async def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> tuple[int, int]:
    """Get pagination parameters with validation"""

    if skip < 0:
        skip = 0

    if limit <= 0 or limit > 1000:
        limit = 100

    return skip, limit


async def validate_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> tuple[Optional[str], Optional[str]]:
    """Validate date range parameters"""

    if start_date and end_date:
        from datetime import datetime

        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            if start_dt >= end_dt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start date must be before end date"
                )

            # Limit range to 1 year
            if (end_dt - start_dt).days > 365:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Date range cannot exceed 1 year"
                )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SSZ"
            )

    return start_date, end_date