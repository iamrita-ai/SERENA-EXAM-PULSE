import logging
from datetime import datetime
from telegram.ext import Application
from telegram.constants import ParseMode
from ..config import config

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


async def send_profile_log(app: Application, user_doc: dict):
    """Send resume-style profile to log channel."""
    if not config.log_channel_id:
        return

    lines = [
        "📋 <b>New / Updated User Profile</b>",
        "",
        f"<b>Name:</b> {user_doc.get('full_name')}",
        f"<b>Telegram:</b> @{user_doc.get('username') or 'N/A'} (ID: <code>{user_doc['tg_id']}</code>)",
        f"<b>State:</b> {user_doc.get('state')}",
        f"<b>Category:</b> {user_doc.get('category')}",
        f"<b>Age:</b> {user_doc.get('age')}",
    ]

    quals = user_doc.get("qualifications", [])
    if quals:
        lines.append("<b>Qualifications:</b>")
        for q in quals:
            lines.append(f" • {q.get('text')}")
    else:
        lines.append("<b>Qualifications:</b> N/A")

    extra = user_doc.get("extra_details")
    if extra:
        lines.append("")
        lines.append(f"<b>Extra Details:</b>\n{extra}")

    lines.append("")
    lines.append(f"<i>Updated at:</i> {datetime.utcnow().isoformat()} UTC")

    text = "\n".join(lines)

    try:
        await app.bot.send_message(
            chat_id=config.log_channel_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error("Failed to send profile log: %s", e)
