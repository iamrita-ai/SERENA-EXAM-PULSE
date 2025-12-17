from telegram import Update
from telegram.ext import ContextTypes
from ..config import config
from ..models.user import (
    get_user_stats,
    list_users,
    get_all_active_users_cursor,
    block_user,
)
from telegram.error import Forbidden


def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return

    stats = get_user_stats()
    text = (
        "📊 <b>Bot Status</b>\n\n"
        f"Total users: <b>{stats['total']}</b>\n"
        f"Blocked users: <b>{stats['blocked']}</b>\n"
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return

    users = list_users(limit=50)
    if not users:
        await update.effective_message.reply_text("No users found.")
        return

    lines = ["👥 <b>Users (first 50)</b>:", ""]
    for u in users:
        line = f"- {u.get('full_name') or 'Unknown'} (ID: {u['tg_id']})"
        if u.get("username"):
            line += f" @{u['username']}"
        lines.append(line)

    await update.effective_message.reply_text(
        "\n".join(lines), parse_mode="HTML", disable_web_page_preview=True
    )


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return

    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /broadcast <message>"
        )
        return

    msg_text = " ".join(context.args)
    sent = 0
    failed = 0

    await update.effective_message.reply_text(
        "Broadcast start ho rahi hai... ye process kuch time le sakta hai."
    )

    async for_user_app = context.application  # just alias

    cursor = get_all_active_users_cursor()
    for doc in cursor:
        try:
            await context.bot.send_message(chat_id=doc["tg_id"], text=msg_text)
            sent += 1
        except Forbidden:
            block_user(doc["tg_id"], reason="blocked_during_broadcast")
            failed += 1
        except Exception:
            failed += 1

    await update.effective_message.reply_text(
        f"Broadcast complete.\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed/Blocked: {failed}"
  )
