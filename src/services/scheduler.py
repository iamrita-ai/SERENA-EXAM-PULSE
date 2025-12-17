from datetime import time, timedelta, timezone
import logging
from telegram.ext import Application, ContextTypes
from telegram.error import Forbidden
from ..models.user import get_all_active_users_cursor, block_user
from ..services.notifications import send_eligibility_alerts
from ..config import config

logger = logging.getLogger(__name__)


async def hourly_notifications_job(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    cursor = get_all_active_users_cursor()
    count = 0
    blocked = 0

    for user_doc in cursor:
        try:
            await send_eligibility_alerts(app, user_doc)
            count += 1
        except Forbidden:
            block_user(user_doc["tg_id"], reason="blocked_during_hourly")
            blocked += 1
        except Exception as e:
            logger.error("Error sending notification to %s: %s", user_doc["tg_id"], e)

    logger.info(
        "Hourly notifications job done. Notified=%s, newly_blocked=%s",
        count,
        blocked,
    )


async def daily_maintenance_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Placeholder for:
    - scraping new exams
    - cleaning old data
    - summary logs, etc.
    """
    logger.info("Daily maintenance job executed.")
    # Example: inform logs channel that daily job ran
    if config.log_channel_id:
        await context.bot.send_message(
            chat_id=config.log_channel_id,
            text="🕒 Daily maintenance job executed.",
        )


def setup_scheduled_jobs(application: Application):
    job_queue = application.job_queue

    # Hourly notifications (every 1 hour)
    job_queue.run_repeating(
        hourly_notifications_job,
        interval=3600,  # seconds
        first=10,  # start after 10 seconds
        name="hourly_notifications",
    )

    # Daily maintenance at 09:00 UTC (adjust as per your timezone)
    job_queue.run_daily(
        daily_maintenance_job,
        time=time(hour=9, minute=0, tzinfo=timezone.utc),
        name="daily_maintenance",
    )

    logger.info("Scheduled jobs registered.")
