from telegram import Update
from telegram.ext import ContextTypes

from ..config import config
from ..services.exams_service import ingest_exam_from_channel_message
from ..services.notifications import notify_users_about_new_exam


async def exam_channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tumhare EXAM_FEED_CHANNEL me post hone wale naye messages ko handle karega.
    - Message ko exams collection me save karta hai
    - Turant eligible users ko wo exam bhej deta hai
    """
    msg = update.channel_post
    if msg is None:
        # Hum sirf channel_post updates handle kar rahe hain
        return

    # Agar EXAM_FEED_CHANNEL_ID set nahi hai to ignore
    if not config.exam_feed_channel_id:
        return

    if msg.chat.id != config.exam_feed_channel_id:
        return

    # Save to DB
    exam_doc = ingest_exam_from_channel_message(msg)
    if not exam_doc:
        return

    # Notify eligible users
    await notify_users_about_new_exam(context.application, exam_doc)
