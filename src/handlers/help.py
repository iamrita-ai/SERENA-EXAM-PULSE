from telegram import Update
from telegram.ext import ContextTypes
from ..models.user import is_blocked


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_blocked(user.id):
        return

    text = (
        "<b>Serena Exam Pulse – Help</b>\n\n"
        "Available commands:\n"
        "/start - Welcome menu\n"
        "/profile - Aapki saved profile dekhne ke liye\n"
        "/editprofile - Profile create / update wizard\n"
        "/settings - Notification & profile settings\n"
        "/help - Yeh help message\n\n"
        "<b>Admin only:</b>\n"
        "/status - Total users + blocked users\n"
        "/users - List of users (first 50)\n"
        "/broadcast &lt;message&gt; - Send message to all users\n"
    )

    await update.effective_message.reply_text(text, parse_mode="HTML")
