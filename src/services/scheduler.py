import logging
from datetime import time, timezone

from telegram.error import Forbidden
from telegram.ext import Application, ContextTypes

from ..config import config
from ..models.user import get_all_active_users_cursor, block_user
from .notifications import send_eligibility_alerts

logger = logging.getLogger(__name__)


async def hourly_notifications_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Har ghante chalne wala job:
    - sab active users ke liye eligibility check
    - naye exams/jobs ki notification bhejna
    """
    app = context.application
    cursor = get_all_active_users_cursor()
    count = 0
    blocked = 0

    for user_doc in cursor:
        tg_id = user_doc["tg_id"]
        try:
            await send_eligibility_alerts(app, user_doc)
            count += 1
        except Forbidden:
            # User ne bot block kar diya
            block_user(tg_id, reason="blocked_during_hourly")
            blocked += 1
        except Exception as e:
            logger.error("Error sending notification to %s: %s", tg_id, e)

    logger.info(
        "Hourly notifications job done. Notified=%s, newly_blocked=%s",
        count,
        blocked,
    )


async def daily_maintenance_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Roz ek baar chalne wala job:
    - future me: scrape new exams
    - purane data cleanup
    - summary logs etc.
    """
    logger.info("Daily maintenance job executed.")

    if config.log_channel_id:
        try:
            await context.bot.send_message(
                chat_id=config.log_channel_id,
                text="🕒 Daily maintenance job executed.",
            )
        except Exception as e:
            logger.error("Failed to send daily maintenance log: %s", e)


def setup_scheduled_jobs(application: Application):
    """
    Application ke JobQueue me hourly & daily jobs register kare.
    """
    job_queue = application.job_queue

    if job_queue is None:
        # Agar python-telegram-bot[job-queue] install nahi hoga to yahan aayega.
        logger.warning(
            "JobQueue is not available. Scheduler disabled. "
            "Install PTB with job-queue extra: pip install \"python-telegram-bot[job-queue]\""
        )
        return

    # Hourly job – har 3600 seconds me
    job_queue.run_repeating(
        hourly_notifications_job,
        interval=3600,  # seconds
        first=10,       # bot start hone ke 10s baad first run
        name="hourly_notifications",
    )

    # Daily job – roz 09:00 UTC
    job_queue.run_daily(
        daily_maintenance_job,
        time=time(hour=9, minute=0, tzinfo=timezone.utc),
        name="daily_maintenance",
    )

    logger.info("Scheduled jobs registered.")
