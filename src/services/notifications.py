from datetime import datetime
from typing import Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application
from ..database import get_users_collection
from .exams_service import get_eligible_exams_for_user

users_col = get_users_collection()


async def send_eligibility_alerts(app: Application, user_doc: Dict[str, Any]):
    eligible = get_eligible_exams_for_user(user_doc)
    if not eligible:
        return

    already = set(user_doc.get("notified_exam_ids") or [])
    new_ids = []

    for exam in eligible:
        if exam["id"] in already:
            continue

        text = (
            f"📢 <b>{exam['title']}</b>\n"
            f"<b>Type:</b> {exam['type']} | <b>Org:</b> {exam['org']}\n"
            f"<b>Salary:</b> {exam['salary']}\n\n"
            f"{exam['details']}\n"
        )

        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Apply Now", url=exam["apply_link"])]]
        )

        await app.bot.send_message(
            chat_id=user_doc["tg_id"], text=text, parse_mode="HTML", reply_markup=kb
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
