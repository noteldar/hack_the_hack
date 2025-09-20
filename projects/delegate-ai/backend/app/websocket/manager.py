import json
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationPriority
from app.schemas.notification import NotificationCreate

websocket_router = APIRouter()
security = HTTPBearer()


class WebSocketManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket for a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket for a user"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            # Remove user entry if no active connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            # Send to all connections for this user (multiple devices)
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(message)
                except:
                    # Remove disconnected websocket
                    self.active_connections[user_id].remove(websocket)

    async def send_notification(self, user_id: int, notification: dict):
        """Send a notification to a specific user"""
        message = {
            "type": "notification",
            "data": notification
        }
        await self.send_personal_message(json.dumps(message), user_id)

    async def send_task_update(self, user_id: int, task_data: dict):
        """Send a task update to a specific user"""
        message = {
            "type": "task_update",
            "data": task_data
        }
        await self.send_personal_message(json.dumps(message), user_id)

    async def send_meeting_update(self, user_id: int, meeting_data: dict):
        """Send a meeting update to a specific user"""
        message = {
            "type": "meeting_update",
            "data": meeting_data
        }
        await self.send_personal_message(json.dumps(message), user_id)

    async def send_agent_update(self, user_id: int, agent_data: dict):
        """Send an agent activity update to a specific user"""
        message = {
            "type": "agent_update",
            "data": agent_data
        }
        await self.send_personal_message(json.dumps(message), user_id)

    def get_active_users(self) -> List[int]:
        """Get list of users with active WebSocket connections"""
        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, []))


# Global WebSocket manager instance
manager = WebSocketManager()


async def get_current_user_ws(token: str, db: AsyncSession) -> User:
    """Get current user from WebSocket token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


@websocket_router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, token: str, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time communication"""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)
        await manager.connect(websocket, user.id)

        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "data": {
                "message": "Connected to Delegate.ai WebSocket",
                "user_id": user.id
            }
        }
        await websocket.send_text(json.dumps(welcome_message))

        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    # Respond to ping with pong
                    pong_message = {"type": "pong", "data": {"timestamp": message.get("timestamp")}}
                    await websocket.send_text(json.dumps(pong_message))

                elif message.get("type") == "subscribe":
                    # Handle subscription to specific events
                    subscription_types = message.get("data", {}).get("events", [])
                    response = {
                        "type": "subscription_confirmed",
                        "data": {"events": subscription_types}
                    }
                    await websocket.send_text(json.dumps(response))

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                # Handle invalid JSON
                error_message = {
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }
                await websocket.send_text(json.dumps(error_message))

    except HTTPException:
        # Authentication failed
        await websocket.close(code=1008)  # Policy violation
    except WebSocketDisconnect:
        pass
    finally:
        # Clean up connection
        if 'user' in locals():
            manager.disconnect(websocket, user.id)


@websocket_router.get("/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_users": manager.get_active_users(),
        "total_connections": sum(
            manager.get_connection_count(user_id)
            for user_id in manager.get_active_users()
        )
    }