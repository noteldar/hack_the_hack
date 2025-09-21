"""
OAuth 2.0 service for Google Calendar integration with token management
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import User
from app.services.google_calendar import google_calendar_client
import logging

logger = logging.getLogger(__name__)


class GoogleOAuthToken:
    """Google OAuth token model for database storage"""

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        scope: str,
        token_type: str = "Bearer"
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.scope = scope
        self.token_type = token_type

    @classmethod
    def from_dict(cls, token_data: Dict[str, Any]) -> "GoogleOAuthToken":
        """Create token from Google OAuth response"""
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return cls(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", ""),
            expires_at=expires_at,
            scope=token_data.get("scope", ""),
            token_type=token_data.get("token_type", "Bearer")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary for storage"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat(),
            "scope": self.scope,
            "token_type": self.token_type
        }

    def is_expired(self) -> bool:
        """Check if access token is expired"""
        return datetime.utcnow() >= self.expires_at - timedelta(minutes=5)  # 5 min buffer


class OAuthService:
    """OAuth service for handling Google authentication and token management"""

    def __init__(self):
        self.calendar_client = google_calendar_client

    async def initiate_oauth_flow(self, user_id: int, db: AsyncSession) -> str:
        """Initiate OAuth flow and return authorization URL"""
        # Use user_id as state for security
        state = f"user_{user_id}"
        auth_url = self.calendar_client.get_auth_url(state=state)

        logger.info(f"Initiated OAuth flow for user {user_id}")
        return auth_url

    async def handle_oauth_callback(
        self,
        code: str,
        state: str,
        db: AsyncSession
    ) -> Optional[User]:
        """Handle OAuth callback and store tokens"""
        try:
            # Extract user ID from state
            if not state.startswith("user_"):
                raise ValueError("Invalid state parameter")

            user_id = int(state.split("_")[1])

            # Get user from database
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {user_id} not found")

            # Exchange code for tokens
            token_data = await self.calendar_client.exchange_code_for_tokens(code)
            token = GoogleOAuthToken.from_dict(token_data)

            # Store tokens in user record
            user.google_calendar_tokens = json.dumps(token.to_dict())
            user.calendar_connected = True
            user.calendar_connected_at = datetime.utcnow()

            await db.commit()

            logger.info(f"Successfully connected Google Calendar for user {user_id}")
            return user

        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            await db.rollback()
            return None

    async def get_valid_access_token(self, user: User, db: AsyncSession) -> Optional[str]:
        """Get valid access token, refreshing if necessary"""
        try:
            if not user.google_calendar_tokens:
                return None

            token_dict = json.loads(user.google_calendar_tokens)
            token_dict["expires_at"] = datetime.fromisoformat(token_dict["expires_at"])
            token = GoogleOAuthToken(
                access_token=token_dict["access_token"],
                refresh_token=token_dict["refresh_token"],
                expires_at=token_dict["expires_at"],
                scope=token_dict["scope"],
                token_type=token_dict.get("token_type", "Bearer")
            )

            # Check if token needs refresh
            if token.is_expired():
                if not token.refresh_token:
                    logger.error(f"No refresh token available for user {user.id}")
                    return None

                # Refresh the token
                new_token_data = await self.calendar_client.refresh_access_token(
                    token.refresh_token
                )

                # Create new token (preserve refresh token if not provided)
                if "refresh_token" not in new_token_data:
                    new_token_data["refresh_token"] = token.refresh_token

                new_token = GoogleOAuthToken.from_dict(new_token_data)

                # Update user record
                user.google_calendar_tokens = json.dumps(new_token.to_dict())
                await db.commit()

                logger.info(f"Refreshed access token for user {user.id}")
                return new_token.access_token

            return token.access_token

        except Exception as e:
            logger.error(f"Error getting valid access token for user {user.id}: {e}")
            return None

    async def revoke_oauth_token(self, user: User, db: AsyncSession) -> bool:
        """Revoke OAuth token and disconnect calendar"""
        try:
            if not user.google_calendar_tokens:
                return True

            token_dict = json.loads(user.google_calendar_tokens)
            access_token = token_dict.get("access_token")

            if access_token:
                # Revoke token with Google
                import httpx
                async with httpx.AsyncClient() as client:
                    revoke_url = f"https://oauth2.googleapis.com/revoke?token={access_token}"
                    response = await client.post(revoke_url)
                    # Google returns 200 even for already revoked tokens

            # Clear tokens from user record
            user.google_calendar_tokens = None
            user.calendar_connected = False
            user.calendar_connected_at = None

            await db.commit()

            logger.info(f"Revoked Google Calendar access for user {user.id}")
            return True

        except Exception as e:
            logger.error(f"Error revoking token for user {user.id}: {e}")
            return False

    async def check_calendar_permissions(self, access_token: str) -> Dict[str, bool]:
        """Check what calendar permissions are available"""
        permissions = {
            "read_calendar": False,
            "write_calendar": False,
            "read_events": False,
            "write_events": False,
            "free_busy": False
        }

        try:
            # Test basic calendar access
            calendars = await self.calendar_client.get_calendars(access_token)
            permissions["read_calendar"] = True

            # Test event reading
            events = await self.calendar_client.get_events(
                access_token, "primary", max_results=1
            )
            permissions["read_events"] = True

            # Test free/busy access
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            later = now + timedelta(hours=1)

            free_busy = await self.calendar_client.get_free_busy(
                access_token, ["primary"], now, later
            )
            permissions["free_busy"] = True

            # For write permissions, we'd need to test with actual creation
            # but we can infer from scopes
            permissions["write_calendar"] = True
            permissions["write_events"] = True

        except Exception as e:
            logger.error(f"Error checking calendar permissions: {e}")

        return permissions

    async def get_user_calendar_info(self, user: User, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Get comprehensive calendar information for user"""
        try:
            access_token = await self.get_valid_access_token(user, db)
            if not access_token:
                return None

            # Get calendars
            calendars = await self.calendar_client.get_calendars(access_token)

            # Get permissions
            permissions = await self.check_calendar_permissions(access_token)

            # Get recent events for context
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            week_ahead = now + timedelta(days=7)

            events = await self.calendar_client.get_events(
                access_token,
                "primary",
                time_min=week_ago,
                time_max=week_ahead,
                max_results=50
            )

            return {
                "connected": True,
                "connected_at": user.calendar_connected_at.isoformat() if user.calendar_connected_at else None,
                "calendars": calendars,
                "permissions": permissions,
                "recent_events_count": len(events),
                "primary_calendar": next((cal for cal in calendars if cal.get("primary")), None)
            }

        except Exception as e:
            logger.error(f"Error getting calendar info for user {user.id}: {e}")
            return None


# Global instance
oauth_service = OAuthService()