import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .worker import celery_app
from app.core.database import AsyncSessionLocal
from app.models.email import Email, EmailStatus
from app.models.meeting import Meeting
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.websocket.manager import manager


async def get_async_db():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@celery_app.task(bind=True)
def process_email_task(self, email_id: int):
    """Process email with AI for task extraction and summarization"""
    async def _process_email():
        async for db in get_async_db():
            # Get email
            result = await db.execute(select(Email).where(Email.id == email_id))
            email = result.scalar_one_or_none()

            if not email:
                return {"error": "Email not found"}

            try:
                # Simulate AI processing (replace with actual AI calls)
                ai_summary = f"Summary of email: {email.subject}"
                ai_sentiment = "neutral"
                ai_category = "general"
                ai_extracted_tasks = []

                # Update email with AI results
                email.ai_summary = ai_summary
                email.ai_sentiment = ai_sentiment
                email.ai_category = ai_category
                email.ai_extracted_tasks = ai_extracted_tasks
                email.ai_confidence = 85
                email.status = EmailStatus.PROCESSED
                email.processed_at = datetime.utcnow()

                await db.commit()

                # Send notification via WebSocket
                notification_data = {
                    "id": f"email_{email_id}",
                    "type": "email_processed",
                    "title": "Email Processed",
                    "message": f"Email '{email.subject}' has been processed by AI",
                    "email_id": email_id
                }
                await manager.send_notification(email.user_id, notification_data)

                return {"success": True, "email_id": email_id}

            except Exception as e:
                email.status = EmailStatus.READ  # Mark as read if processing failed
                await db.commit()
                return {"error": str(e)}

    return asyncio.run(_process_email())


@celery_app.task(bind=True)
def prepare_meeting_task(self, meeting_id: int):
    """Prepare meeting with AI briefing"""
    async def _prepare_meeting():
        async for db in get_async_db():
            # Get meeting
            result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
            meeting = result.scalar_one_or_none()

            if not meeting:
                return {"error": "Meeting not found"}

            try:
                # Simulate AI meeting preparation
                ai_briefing = f"""
                Meeting Briefing for: {meeting.title}

                Agenda:
                {meeting.agenda or "No agenda provided"}

                Preparation Notes:
                - Review attendee backgrounds
                - Prepare key discussion points
                - Set meeting objectives

                Recommended Duration: {(meeting.end_time - meeting.start_time).total_seconds() / 60} minutes
                """

                meeting.ai_briefing = ai_briefing
                meeting.preparation_notes = "AI preparation completed"
                await db.commit()

                # Send notification
                notification_data = {
                    "id": f"meeting_{meeting_id}",
                    "type": "meeting_prepared",
                    "title": "Meeting Prepared",
                    "message": f"Meeting '{meeting.title}' has been prepared by AI",
                    "meeting_id": meeting_id
                }
                await manager.send_notification(meeting.user_id, notification_data)

                return {"success": True, "meeting_id": meeting_id}

            except Exception as e:
                return {"error": str(e)}

    return asyncio.run(_prepare_meeting())


@celery_app.task(bind=True)
def sync_calendar_task(self, user_id: int, provider: str):
    """Sync calendar with external provider"""
    async def _sync_calendar():
        # This would integrate with Google Calendar API or Microsoft Graph API
        # For now, simulate the sync process
        try:
            # Simulate calendar sync
            await asyncio.sleep(2)  # Simulate API calls

            sync_result = {
                "success": True,
                "provider": provider,
                "events_synced": 5,
                "events_added": 2,
                "events_updated": 3,
                "sync_time": datetime.utcnow().isoformat()
            }

            # Send notification
            notification_data = {
                "id": f"calendar_sync_{user_id}",
                "type": "calendar_sync",
                "title": "Calendar Synced",
                "message": f"Calendar sync with {provider} completed successfully",
                "data": sync_result
            }
            await manager.send_notification(user_id, notification_data)

            return sync_result

        except Exception as e:
            return {"error": str(e)}

    return asyncio.run(_sync_calendar())


@celery_app.task(bind=True)
def extract_tasks_from_email(self, email_id: int):
    """Extract actionable tasks from email content"""
    async def _extract_tasks():
        async for db in get_async_db():
            result = await db.execute(select(Email).where(Email.id == email_id))
            email = result.scalar_one_or_none()

            if not email:
                return {"error": "Email not found"}

            try:
                # Simulate AI task extraction
                extracted_tasks = [
                    {
                        "title": "Follow up on project status",
                        "description": f"Based on email from {email.sender_email}",
                        "priority": "medium",
                        "confidence": 0.85
                    },
                    {
                        "title": "Schedule meeting",
                        "description": "Set up meeting discussed in email",
                        "priority": "high",
                        "confidence": 0.92
                    }
                ]

                # Update email with extracted tasks
                email.ai_extracted_tasks = extracted_tasks
                await db.commit()

                # Send notification
                notification_data = {
                    "id": f"tasks_extracted_{email_id}",
                    "type": "tasks_extracted",
                    "title": "Tasks Extracted",
                    "message": f"Found {len(extracted_tasks)} actionable tasks in email",
                    "email_id": email_id,
                    "tasks": extracted_tasks
                }
                await manager.send_notification(email.user_id, notification_data)

                return {"success": True, "tasks_count": len(extracted_tasks)}

            except Exception as e:
                return {"error": str(e)}

    return asyncio.run(_extract_tasks())


@celery_app.task(bind=True)
def send_notification_task(self, user_id: int, notification_data: Dict[str, Any]):
    """Send notification to user"""
    async def _send_notification():
        try:
            # Send via WebSocket
            await manager.send_notification(user_id, notification_data)

            # Here you could also send email/push notifications

            return {"success": True, "user_id": user_id}
        except Exception as e:
            return {"error": str(e)}

    return asyncio.run(_send_notification())


# Periodic tasks
@celery_app.task
def sync_all_calendars():
    """Sync calendars for all active users"""
    async def _sync_all():
        async for db in get_async_db():
            # Get all active users
            result = await db.execute(select(User).where(User.is_active == True))
            users = result.scalars().all()

            synced_count = 0
            for user in users:
                # Check if user has calendar providers configured
                if user.google_id:
                    sync_calendar_task.delay(user.id, "google")
                    synced_count += 1
                if user.microsoft_id:
                    sync_calendar_task.delay(user.id, "microsoft")
                    synced_count += 1

            return {"synced_users": synced_count}

    return asyncio.run(_sync_all())


@celery_app.task
def process_pending_emails():
    """Process pending emails that need AI analysis"""
    async def _process_pending():
        async for db in get_async_db():
            # Get unprocessed emails
            result = await db.execute(
                select(Email).where(Email.status == EmailStatus.UNREAD)
                .limit(10)  # Process up to 10 emails at a time
            )
            emails = result.scalars().all()

            processed_count = 0
            for email in emails:
                process_email_task.delay(email.id)
                processed_count += 1

            return {"processed_count": processed_count}

    return asyncio.run(_process_pending())


@celery_app.task
def cleanup_old_notifications():
    """Clean up old read notifications"""
    async def _cleanup():
        async for db in get_async_db():
            # Delete read notifications older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            result = await db.execute(
                select(Notification).where(
                    and_(
                        Notification.is_read == True,
                        Notification.created_at < cutoff_date
                    )
                )
            )
            old_notifications = result.scalars().all()

            for notification in old_notifications:
                await db.delete(notification)

            await db.commit()
            return {"cleaned_up": len(old_notifications)}

    return asyncio.run(_cleanup())