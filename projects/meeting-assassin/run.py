#!/usr/bin/env python3
"""
Quick startup script for MeetingAssassin
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting MeetingAssassin API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔗 WebSocket Test: http://localhost:8000/ws-test")
    print("⚡ Use Ctrl+C to stop the server\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )