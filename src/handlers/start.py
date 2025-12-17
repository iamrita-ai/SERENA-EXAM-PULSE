from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.main_menu import get_start_keyboard
from ..models.user import is_blocked


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_blocked(user.id):
        return

    text = (
        "✨ <b>Serena Exam Pulse</b>\n\n"
        "Personalized exam & job notification bot.\n\n"
        "➡️ Apni exam profile banane ke liye niche ka button use karein."
    )

    await update.effective_message.reply_text(
        text, reply_markup=get_start_keyboard(), parse_mode="HTML"
    )
