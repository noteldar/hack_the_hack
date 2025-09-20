#!/usr/bin/env python3
"""
Validation script to check if the Delegate.ai backend is set up correctly.
"""

import sys
import os
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists and print status."""
    if os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} - NOT FOUND")
        return False

def main():
    """Main validation function."""
    print("🔍 Validating Delegate.ai Backend Setup...")
    print("=" * 50)

    all_good = True

    # Check core configuration files
    core_files = [
        ("requirements.txt", "Requirements file"),
        (".env.example", "Environment template"),
        ("Dockerfile", "Docker configuration"),
        ("docker-compose.yml", "Docker Compose configuration"),
        ("alembic.ini", "Alembic configuration"),
        ("pyproject.toml", "Project configuration"),
        ("Makefile", "Build configuration"),
        ("README.md", "Documentation"),
    ]

    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_good = False

    # Check main application structure
    app_dirs = [
        ("app/", "Main application directory"),
        ("app/api/", "API directory"),
        ("app/api/v1/", "API v1 directory"),
        ("app/api/v1/endpoints/", "API endpoints directory"),
        ("app/auth/", "Authentication directory"),
        ("app/background_jobs/", "Background jobs directory"),
        ("app/core/", "Core directory"),
        ("app/models/", "Models directory"),
        ("app/schemas/", "Schemas directory"),
        ("app/services/", "Services directory"),
        ("app/websocket/", "WebSocket directory"),
        ("alembic/", "Alembic directory"),
        ("alembic/versions/", "Alembic versions directory"),
        ("tests/", "Tests directory"),
        ("scripts/", "Scripts directory"),
    ]

    for dir_path, description in app_dirs:
        if not check_directory_exists(dir_path, description):
            all_good = False

    # Check critical application files
    app_files = [
        ("app/main.py", "Main FastAPI application"),
        ("app/core/config.py", "Configuration module"),
        ("app/core/database.py", "Database configuration"),
        ("app/core/security.py", "Security utilities"),
        ("app/core/redis.py", "Redis configuration"),
        ("app/api/v1/api.py", "Main API router"),
        ("app/auth/oauth.py", "OAuth implementation"),
        ("app/auth/deps.py", "Authentication dependencies"),
        ("app/background_jobs/worker.py", "Celery worker"),
        ("app/background_jobs/tasks.py", "Background tasks"),
        ("app/websocket/manager.py", "WebSocket manager"),
        ("alembic/env.py", "Alembic environment"),
        ("tests/conftest.py", "Test configuration"),
        ("scripts/start.sh", "Start script"),
    ]

    for file_path, description in app_files:
        if not check_file_exists(file_path, description):
            all_good = False

    # Check models
    model_files = [
        ("app/models/__init__.py", "Models init"),
        ("app/models/user.py", "User model"),
        ("app/models/meeting.py", "Meeting model"),
        ("app/models/task.py", "Task model"),
        ("app/models/email.py", "Email model"),
        ("app/models/agent.py", "Agent models"),
        ("app/models/notification.py", "Notification model"),
    ]

    for file_path, description in model_files:
        if not check_file_exists(file_path, description):
            all_good = False

    # Check schemas
    schema_files = [
        ("app/schemas/__init__.py", "Schemas init"),
        ("app/schemas/user.py", "User schemas"),
        ("app/schemas/meeting.py", "Meeting schemas"),
        ("app/schemas/task.py", "Task schemas"),
        ("app/schemas/email.py", "Email schemas"),
        ("app/schemas/agent.py", "Agent schemas"),
        ("app/schemas/notification.py", "Notification schemas"),
        ("app/schemas/auth.py", "Auth schemas"),
    ]

    for file_path, description in schema_files:
        if not check_file_exists(file_path, description):
            all_good = False

    # Check API endpoints
    endpoint_files = [
        ("app/api/v1/endpoints/auth.py", "Auth endpoints"),
        ("app/api/v1/endpoints/users.py", "Users endpoints"),
        ("app/api/v1/endpoints/tasks.py", "Tasks endpoints"),
        ("app/api/v1/endpoints/meetings.py", "Meetings endpoints"),
        ("app/api/v1/endpoints/emails.py", "Emails endpoints"),
        ("app/api/v1/endpoints/calendar.py", "Calendar endpoints"),
        ("app/api/v1/endpoints/agents.py", "Agents endpoints"),
    ]

    for file_path, description in endpoint_files:
        if not check_file_exists(file_path, description):
            all_good = False

    # Check services
    service_files = [
        ("app/services/__init__.py", "Services init"),
        ("app/services/user.py", "User service"),
        ("app/services/task.py", "Task service"),
        ("app/services/meeting.py", "Meeting service"),
        ("app/services/email.py", "Email service"),
        ("app/services/agent.py", "Agent service"),
        ("app/services/calendar.py", "Calendar service"),
    ]

    for file_path, description in service_files:
        if not check_file_exists(file_path, description):
            all_good = False

    print("=" * 50)

    if all_good:
        print("🎉 All files and directories are present!")
        print("🚀 Your Delegate.ai backend is ready!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Set up PostgreSQL and Redis")
        print("3. Run: make dev-setup")
        print("4. Run: make migrate")
        print("5. Run: make run")
        print("\nOr use Docker:")
        print("docker-compose up --build")
        return 0
    else:
        print("❌ Some files or directories are missing!")
        print("Please check the setup and ensure all components are created.")
        return 1

if __name__ == "__main__":
    sys.exit(main())