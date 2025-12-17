
from telegram import Update
from telegram.ext import ContextTypes

from ..models.user import get_user_by_tg_id, is_blocked
from ..services.exams_service import get_eligible_exams_for_user, build_exam_message_and_keyboard
from ..services.force_sub import ensure_subscribed


async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /jobs (ya /job) command:
    - User ki profile check karega
    - DB me recent exams/jobs me se matching list nikaalega
    - Har ek ko attractive format me bhejega.
    """
    user = update.effective_user
    if is_blocked(user.id):
        return

    # Force-subscribe check
    ok = await ensure_subscribed(update, context)
    if not ok:
        return

    user_doc = get_user_by_tg_id(user.id)
    if not user_doc:
        await update.effective_message.reply_text(
            "Aapki profile abhi create nahi hui hai.\n"
            "📝 Pehle /editprofile use karke apni exam profile banaiye."
        )
        return

    eligible = get_eligible_exams_for_user(user_doc)

    if not eligible:
        await update.effective_message.reply_text(
            "Abhi aapki profile ke hisaab se koi matching Govt exam / Job nahi mili.\n"
            "♦ Age, qualification aur notifications settings check kar sakte hain via /settings."
        )
        return

    # Summary message
    await update.effective_message.reply_text(
        f"✅ Aapki profile ke hisaab se <b>{len(eligible)}</b> current Govt Exams / Jobs mil gayi hain.\n"
        "Har ek ka detail alag message me bhej raha hoon:",
        parse_mode="HTML",
    )

    for exam in eligible:
        text, kb = build_exam_message_and_keyboard(exam)
        await update.effective_chat.send_message(
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
        )
