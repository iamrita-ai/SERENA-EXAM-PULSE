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
      sab ek-ek karke attractive format me bhej dega.
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
        f"✅ Aapki profile ke hisaab se <b>{len(eligible)}</b> current Govt Exams / Jobs mil gayi hain.\n"
        "Har ek ka detail alag message me bhej raha hoon:",
        parse_mode="HTML",
    )

    # Har exam/job ek-ek message + Apply + Notification buttons
    for exam in eligible:
        title = exam["title"]
        ex_type = exam["type"]
        org = exam["org"]
        salary = exam.get("salary")
        notif_date = exam.get("notification_date")
        form_start = exam.get("form_start")
        form_end = exam.get("form_end")
        min_age = exam.get("min_age")
        max_age = exam.get("max_age")
        details = exam.get("details")

        lines = [
            f"📢 <b>{title}</b>",
            f"🏛 <b>Type:</b> {ex_type}   |   🏢 <b>Org:</b> {org}",
        ]

        if salary:
            lines.append(f"💰 <b>Salary:</b> {salary}")

        if notif_date:
            lines.append(f"📅 <b>Notification:</b> {notif_date}")

        if form_start or form_end:
            form_parts = []
            if form_start:
                form_parts.append(f"Start: {form_start}")
            if form_end:
                form_parts.append(f"Last Date: {form_end}")
            lines.append("📝 <b>Form Dates:</b> " + " | ".join(form_parts))

        if min_age or max_age:
            age_parts = []
            if min_age:
                age_parts.append(f"Min {min_age}")
            if max_age:
                age_parts.append(f"Max {max_age}")
            lines.append("🎯 <b>Age Limit:</b> " + " | ".join(age_parts))

        if details:
            lines.append("")
            lines.append(details)

        text = "\n".join(lines)

        buttons_row = []
        apply_link = exam.get("apply_link")
        if apply_link:
            buttons_row.append(
                InlineKeyboardButton(
                    "🔗 Apply Now",
                    url=apply_link.strip(),
                )
            )

        source_link = exam.get("source_link")
        if source_link:
            buttons_row.append(
                InlineKeyboardButton(
                    "📄 Official Notification",
                    url=source_link.strip(),
                )
            )

        kb = InlineKeyboardMarkup([buttons_row]) if buttons_row else None

        await update.effective_chat.send_message(
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
        )
