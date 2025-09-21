"""
MeetingAssassin - AI Productivity Agent
FastAPI backend for hackathon development
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager
from typing import List

from app.core.config import settings
from app.core.websocket import WebSocketManager
from app.api.v1 import api_router
from app.models.database import init_db
from app.api.avatar_endpoints import router as avatar_router
from app.avatar.demo.demo_scenarios import DemoScenarioManager


# WebSocket manager instance
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()

    # Initialize demo scenarios
    app.state.demo_manager = DemoScenarioManager()

    print("🚀 MeetingAssassin backend started!")
    print("🤖 AI Avatar System initialized!")
    print("🎯 Demo scenarios loaded!")
    yield
    # Shutdown
    print("👋 MeetingAssassin backend shutting down...")


app = FastAPI(
    title="MeetingAssassin API",
    description="AI Meeting Avatar System - Autonomous Meeting Participation with GPT-4o",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Include Avatar API routes
app.include_router(avatar_router)


@app.get("/")
async def root():
    """Health check endpoint with AI Avatar status"""
    return {
        "message": "MeetingAssassin AI Avatar System",
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "ai_avatar": True,
            "real_time_transcription": True,
            "voice_synthesis": True,
            "meeting_intelligence": True,
            "autonomous_participation": True,
            "webrtc_enabled": True
        },
        "demo_scenarios": app.state.demo_manager.get_scenario_list() if hasattr(app.state, 'demo_manager') else []
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - can be extended for specific message handling
            await websocket_manager.send_personal_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)


@app.get("/ws-test")
async def websocket_test():
    """Simple WebSocket test page"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>MeetingAssassin WebSocket Test</title>
        </head>
        <body>
            <h1>WebSocket Test</h1>
            <div id="messages"></div>
            <input type="text" id="messageText" placeholder="Enter a message">
            <button onclick="sendMessage()">Send</button>
            <script>
                const ws = new WebSocket("ws://localhost:8000/ws/test-client");

                ws.onmessage = function(event) {
                    const messages = document.getElementById('messages');
                    messages.innerHTML += '<div>' + event.data + '</div>';
                };

                function sendMessage() {
                    const messageText = document.getElementById('messageText');
                    ws.send(messageText.value);
                    messageText.value = '';
                }
            </script>
        </body>
    </html>
    """)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )