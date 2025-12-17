from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.main_menu import get_start_keyboard
from ..models.user import is_blocked
from ..services.force_sub import ensure_subscribed


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_blocked(user.id):
        # Agar user blocked hai to koi response nahi
        return

    # 🔐 Force Subscribe check
    ok = await ensure_subscribed(update, context)
    if not ok:
        # User ne channel join nahi kiya -> yahin return kar do
        return

    text = (
        "✨ <b>Serena Exam Pulse</b>\n\n"
        "Aapki personalized exam & job alerts assistant.\n\n"
        "📌 Start karne ke liye niche diye gaye buttons use karein."
    )

    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=get_start_keyboard(),
    )
