from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "delegate_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.background_jobs.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "sync-calendars": {
        "task": "app.background_jobs.tasks.sync_all_calendars",
        "schedule": 300.0,  # Every 5 minutes
    },
    "process-pending-emails": {
        "task": "app.background_jobs.tasks.process_pending_emails",
        "schedule": 60.0,  # Every minute
    },
    "cleanup-old-notifications": {
        "task": "app.background_jobs.tasks.cleanup_old_notifications",
        "schedule": 3600.0,  # Every hour
    },
}

# Load tasks
from . import tasks