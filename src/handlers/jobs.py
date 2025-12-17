from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from ..models.user import get_user_by_tg_id, is_blocked
from ..services.exams_service import get_eligible_exams_for_user
from ..services.force_sub import ensure_subscribed


async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /jobs (ya /job) command:
    - User ki profile check karega
    - Current SAMPLE_EXAMS me se jitne exams/jobs criteria match karte hain
      sab ek-ek karke bhej dega, Apply button ke sath
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

    # Pehle ek chhota sa summary message
    await update.effective_message.reply_text(
        f"✅ Aapki profile ke hisaab se {len(eligible)} current Govt Exams / Jobs mil gayi hain.\n"
        "Har ek ka detail alag message me bhej raha hoon:"
    )

    # Har exam/job ek-ek message + Apply button ke sath
    for exam in eligible:
        text_lines = [
            f"📢 <b>{exam['title']}</b>",
            f"<b>Type:</b> {exam['type']} | <b>Org:</b> {exam['org']}",
        ]

        salary = exam.get("salary")
        if salary:
            text_lines.append(f"<b>Salary:</b> {salary}")

        min_age = exam.get("min_age")
        max_age = exam.get("max_age")
        if min_age or max_age:
            age_str = []
            if min_age:
                age_str.append(f"Min {min_age}")
            if max_age:
                age_str.append(f"Max {max_age}")
            text_lines.append(f"<b>Age Limit:</b> " + " | ".join(age_str))

        details = exam.get("details")
        if details:
            text_lines.append("")
            text_lines.append(details)

        text = "\n".join(text_lines)

        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔗 Apply Now",
                        url=exam["apply_link"],
                    )
                ]
            ]
        )

        await update.effective_chat.send_message(
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
      )
