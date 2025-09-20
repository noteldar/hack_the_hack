from typing import Optional
from datetime import datetime
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import Token

# OAuth setup
oauth = OAuth()

# Google OAuth
google_oauth = oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Microsoft OAuth
microsoft_oauth = oauth.register(
    name='microsoft',
    client_id=settings.MICROSOFT_CLIENT_ID,
    client_secret=settings.MICROSOFT_CLIENT_SECRET,
    server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid_configuration',
    client_kwargs={'scope': 'openid email profile'}
)


async def get_or_create_user_from_oauth(
    db: AsyncSession,
    email: str,
    full_name: str,
    avatar_url: Optional[str] = None,
    google_id: Optional[str] = None,
    microsoft_id: Optional[str] = None
) -> User:
    """Get or create user from OAuth data"""

    # Try to find existing user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # Update OAuth IDs if not set
        updated = False
        if google_id and not user.google_id:
            user.google_id = google_id
            updated = True
        if microsoft_id and not user.microsoft_id:
            user.microsoft_id = microsoft_id
            updated = True
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
            updated = True

        if updated:
            user.last_login = datetime.utcnow()
            await db.commit()
            await db.refresh(user)

        return user

    # Create new user
    user_data = UserCreate(
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
        google_id=google_id,
        microsoft_id=microsoft_id
    )

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        avatar_url=user_data.avatar_url,
        google_id=user_data.google_id,
        microsoft_id=user_data.microsoft_id,
        is_active=True,
        last_login=datetime.utcnow()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_oauth_user(
    provider: str,
    user_info: dict,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Authenticate user from OAuth provider"""

    try:
        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('given_name', '') + ' ' + user_info.get('family_name', '')
        avatar_url = user_info.get('picture')

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )

        # Create or get user based on provider
        if provider == 'google':
            google_id = user_info.get('sub')
            user = await get_or_create_user_from_oauth(
                db, email, name, avatar_url, google_id=google_id
            )
        elif provider == 'microsoft':
            microsoft_id = user_info.get('sub') or user_info.get('oid')
            user = await get_or_create_user_from_oauth(
                db, email, name, avatar_url, microsoft_id=microsoft_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider"
            )

        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


# Import dependencies here to avoid circular imports
from .deps import get_current_user, get_current_active_user

__all__ = [
    "google_oauth",
    "microsoft_oauth",
    "authenticate_oauth_user",
    "get_current_user",
    "get_current_active_user"
]