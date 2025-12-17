
from datetime import datetime
from typing import Dict, Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application

from ..database import get_users_collection
from .exams_service import get_eligible_exams_for_user

users_col = get_users_collection()


async def send_eligibility_alerts(app: Application, user_doc: Dict[str, Any]):
    """
    Scheduler / hourly job ke through chalne wala function.
    Pehle se notified exams ko dobara nahi bhejta.
    """
    eligible = get_eligible_exams_for_user(user_doc)
    if not eligible:
        return

    already = set(user_doc.get("notified_exam_ids") or [])
    new_ids = []

    for exam in eligible:
        if exam["id"] in already:
            continue

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

        await app.bot.send_message(
            chat_id=user_doc["tg_id"],
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
        )
        new_ids.append(exam["id"])

    if new_ids:
        users_col.update_one(
            {"tg_id": user_doc["tg_id"]},
            {
                "$addToSet": {"notified_exam_ids": {"$each": new_ids}},
                "$set": {"last_notified_at": datetime.utcnow()},
            },
            )
