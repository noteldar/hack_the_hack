"""
Authentication service
"""

import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.database import get_db
from app.models.user import User


class AuthService:
    """Authentication service for Google OAuth and JWT"""

    def __init__(self):
        self.security = HTTPBearer()

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": code
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for tokens"
                )
            return response.json()

    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"

        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )
            return response.json()

    async def create_or_update_user(self, db: AsyncSession, user_info: Dict[str, Any], token_data: Dict[str, Any]) -> User:
        """Create or update user in database"""
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")

        # Check if user exists
        query = select(User).where(User.google_id == google_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            # Update existing user
            user.access_token = token_data.get("access_token")
            if "refresh_token" in token_data:
                user.refresh_token = token_data.get("refresh_token")
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                avatar_url=user_info.get("picture"),
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                last_login=datetime.utcnow()
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)
        return user

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_current_user(self, token: str = Depends(HTTPBearer()), db: AsyncSession = Depends(get_db)) -> User:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    async def refresh_google_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Google access token"""
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to refresh token"
                )
            return response.json()

    async def revoke_google_token(self, token: str):
        """Revoke Google token"""
        revoke_url = f"https://oauth2.googleapis.com/revoke?token={token}"

        async with httpx.AsyncClient() as client:
            await client.post(revoke_url)

    async def get_user_by_refresh_token(self, db: AsyncSession, refresh_token: str) -> Optional[User]:
        """Get user by refresh token"""
        query = select(User).where(User.refresh_token == refresh_token)
        result = await db.execute(query)
        return result.scalar_one_or_none()