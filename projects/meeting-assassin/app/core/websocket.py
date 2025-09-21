"""
WebSocket manager for real-time updates
"""

from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected via WebSocket")

        # Send welcome message
        await self.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Connected to MeetingAssassin",
                "client_id": client_id
            }),
            client_id
        )

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def send_meeting_update(self, client_id: str, meeting_data: dict):
        """Send meeting-specific updates"""
        message = json.dumps({
            "type": "meeting_update",
            "data": meeting_data,
            "timestamp": meeting_data.get("timestamp")
        })
        await self.send_personal_message(message, client_id)

    async def send_calendar_optimization(self, client_id: str, optimization_data: dict):
        """Send calendar optimization results"""
        message = json.dumps({
            "type": "calendar_optimization",
            "data": optimization_data,
            "fitness_score": optimization_data.get("fitness_score"),
            "generation": optimization_data.get("generation")
        })
        await self.send_personal_message(message, client_id)

    async def send_ai_decision(self, client_id: str, decision_data: dict):
        """Send AI decision updates"""
        message = json.dumps({
            "type": "ai_decision",
            "data": decision_data,
            "avatar_personality": decision_data.get("avatar_personality"),
            "confidence": decision_data.get("confidence")
        })
        await self.send_personal_message(message, client_id)

    async def send_productivity_metrics(self, client_id: str, metrics: dict):
        """Send productivity metrics updates"""
        message = json.dumps({
            "type": "productivity_metrics",
            "data": metrics,
            "timestamp": metrics.get("timestamp")
        })
        await self.send_personal_message(message, client_id)

    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())

    def is_connected(self, client_id: str) -> bool:
        """Check if a client is connected"""
        return client_id in self.active_connections