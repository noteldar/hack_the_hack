# Delegate.ai Backend

A FastAPI backend for Delegate.ai - an autonomous AI Chief of Staff application.

## Features

- **User Authentication**: OAuth2 integration with Google and Microsoft
- **Calendar Integration**: Sync and manage calendar events
- **Email Processing**: AI-powered email analysis and task extraction
- **Task Management**: Create, update, and track tasks
- **Meeting Management**: Schedule and prepare meetings with AI assistance
- **AI Agent System**: Orchestrate various AI agents for different tasks
- **Real-time Communication**: WebSocket support for live updates
- **Background Processing**: Celery-based async task processing
- **Database**: PostgreSQL with async SQLAlchemy
- **Caching**: Redis for caching and task queues

## Tech Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM with PostgreSQL
- **Pydantic V2**: Data validation and serialization
- **Celery**: Background task processing
- **Redis**: Caching and message broker
- **WebSockets**: Real-time communication
- **OAuth2**: Authentication with external providers
- **Alembic**: Database migrations
- **Docker**: Containerization

## Project Structure

```
app/
├── api/                    # API routes
│   └── v1/
│       └── endpoints/      # API endpoint modules
├── auth/                   # Authentication logic
├── background_jobs/        # Celery tasks
├── core/                   # Core configuration
├── models/                 # SQLAlchemy models
├── schemas/               # Pydantic schemas
├── services/              # Business logic
└── websocket/             # WebSocket handlers
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database:
```bash
alembic upgrade head
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `GET /api/v1/auth/google` - Google OAuth login
- `GET /api/v1/auth/microsoft` - Microsoft OAuth login
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user

### Tasks
- `GET /api/v1/tasks/` - List tasks
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}` - Get task
- `PATCH /api/v1/tasks/{id}` - Update task
- `POST /api/v1/tasks/{id}/complete` - Complete task

### Meetings
- `GET /api/v1/meetings/` - List meetings
- `POST /api/v1/meetings/` - Create meeting
- `GET /api/v1/meetings/{id}` - Get meeting
- `PATCH /api/v1/meetings/{id}` - Update meeting
- `POST /api/v1/meetings/{id}/prepare` - Prepare meeting with AI

### Emails
- `GET /api/v1/emails/` - List emails
- `POST /api/v1/emails/` - Import email
- `POST /api/v1/emails/{id}/process` - Process email with AI
- `POST /api/v1/emails/{id}/extract-tasks` - Extract tasks from email

### Calendar
- `GET /api/v1/calendar/events` - Get calendar events
- `POST /api/v1/calendar/sync` - Sync with external calendar
- `GET /api/v1/calendar/availability` - Check availability
- `POST /api/v1/calendar/find-slots` - Find available time slots

### Agents
- `GET /api/v1/agents/` - List AI agents
- `POST /api/v1/agents/` - Create agent
- `POST /api/v1/agents/{id}/execute` - Execute agent task
- `GET /api/v1/agents/{id}/activities` - Get agent activities

### WebSocket
- `WS /ws/connect?token={jwt_token}` - WebSocket connection

## Background Jobs

The system uses Celery for background processing:

- **Email Processing**: AI analysis of incoming emails
- **Meeting Preparation**: Generate AI briefings for meetings
- **Calendar Sync**: Sync with external calendar providers
- **Task Extraction**: Extract actionable tasks from emails
- **Notifications**: Send real-time notifications

### Running Celery

```bash
# Worker
celery -A app.background_jobs.worker worker --loglevel=info

# Beat scheduler (for periodic tasks)
celery -A app.background_jobs.worker beat --loglevel=info
```

## Database Models

- **User**: User accounts with OAuth integration
- **Meeting**: Calendar events and meetings
- **Task**: Tasks and action items
- **Email**: Email messages with AI analysis
- **Agent**: AI agents for automation
- **AgentActivity**: Agent execution history
- **Notification**: Real-time notifications

## WebSocket Events

The WebSocket connection supports these message types:

- `notification`: Real-time notifications
- `task_update`: Task status changes
- `meeting_update`: Meeting updates
- `agent_update`: Agent activity updates

## Development

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/
```

### Testing

```bash
pytest
```

## Deployment

The application is containerized and can be deployed using:

- Docker Compose (development)
- Kubernetes (production)
- Cloud platforms (AWS, GCP, Azure)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.