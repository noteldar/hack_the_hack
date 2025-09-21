"""
Authentication endpoints for Google OAuth
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import httpx
from typing import Dict, Any

from app.core.config import settings
from app.models.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, TokenResponse
from app.services.auth import AuthService

router = APIRouter()
auth_service = AuthService()


@router.get("/google")
async def google_login():
    """Initiate Google OAuth flow"""
    # In a real implementation, generate state parameter for security
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile https://www.googleapis.com/auth/calendar&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange authorization code for tokens
        token_data = await auth_service.exchange_code_for_tokens(code)

        # Get user info from Google
        user_info = await auth_service.get_google_user_info(token_data["access_token"])

        # Create or update user
        user = await auth_service.create_or_update_user(db, user_info, token_data)

        # Generate JWT token for our app
        access_token = auth_service.create_access_token({"sub": user.email})

        # In production, redirect to frontend with token
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh Google access token"""
    try:
        # Find user by refresh token
        user = await auth_service.get_user_by_refresh_token(db, refresh_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Refresh Google tokens
        new_tokens = await auth_service.refresh_google_token(user.refresh_token)

        # Update user tokens
        user.access_token = new_tokens["access_token"]
        if "refresh_token" in new_tokens:
            user.refresh_token = new_tokens["refresh_token"]

        await db.commit()

        return {"message": "Token refreshed successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.get("/me")
async def get_current_user(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get current authenticated user"""
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and revoke tokens"""
    try:
        # Revoke Google tokens
        if current_user.access_token:
            await auth_service.revoke_google_token(current_user.access_token)

        # Clear user tokens
        current_user.access_token = None
        current_user.refresh_token = None
        current_user.token_expires_at = None

        await db.commit()

        return {"message": "Successfully logged out"}

    except Exception as e:
        # Even if token revocation fails, clear local tokens
        current_user.access_token = None
        current_user.refresh_token = None
        current_user.token_expires_at = None
        await db.commit()

        return {"message": "Logged out (some cleanup may have failed)"}


@router.get("/calendar/access")
async def check_calendar_access(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Check if user has granted calendar access"""
    try:
        if not current_user.access_token:
            return {"has_access": False, "message": "No access token"}

        # Try to access calendar API
        credentials = Credentials(token=current_user.access_token)
        service = build('calendar', 'v3', credentials=credentials)

        # Test API access
        calendar_list = service.calendarList().list(maxResults=1).execute()

        return {
            "has_access": True,
            "message": "Calendar access confirmed",
            "calendars_count": len(calendar_list.get('items', []))
        }

    except Exception as e:
        return {
            "has_access": False,
            "message": f"Calendar access failed: {str(e)}"
        }