from datetime import datetime
from typing import Dict, Any

from telegram.ext import Application
from telegram.error import Forbidden

from ..database import get_users_collection
from ..models.user import get_all_active_users_cursor, block_user
from .exams_service import (
    get_eligible_exams_for_user,
    build_exam_message_and_keyboard,
    is_user_eligible_for_exam,
)

users_col = get_users_collection()


async def send_eligibility_alerts(app: Application, user_doc: Dict[str, Any]):
    """
    Scheduler se chalne wala function:
    - recent exams (DB) me se user ke liye eligible nikalta hai
    - jo exams pehle send ho chuke (notified_exam_ids), unko skip karta hai
    """
    eligible = get_eligible_exams_for_user(user_doc)
    if not eligible:
        return

    already = set(user_doc.get("notified_exam_ids") or [])
    new_ids = []

    for exam in eligible:
        ex_id = exam.get("exam_id")
        if not ex_id or ex_id in already:
            continue

        text, kb = build_exam_message_and_keyboard(exam)
        await app.bot.send_message(
            chat_id=user_doc["tg_id"],
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
        )
        new_ids.append(ex_id)

    if new_ids:
        users_col.update_one(
            {"tg_id": user_doc["tg_id"]},
            {
                "$addToSet": {"notified_exam_ids": {"$each": new_ids}},
                "$set": {"last_notified_at": datetime.utcnow()},
            },
        )


async def notify_users_about_new_exam(app: Application, exam_doc: Dict[str, Any]):
    """
    Jab channel me new exam post aaye:
    - turant sab users me se eligible users ko yeh exam bhej do
    - user's notified_exam_ids me exam_id add karo
    """
    ex_id = exam_doc.get("exam_id")
    if not ex_id:
        return

    cursor = get_all_active_users_cursor()
    for user_doc in cursor:
        tg_id = user_doc["tg_id"]
        try:
            if not is_user_eligible_for_exam(user_doc, exam_doc):
                continue

            already = set(user_doc.get("notified_exam_ids") or [])
            if ex_id in already:
                continue

            text, kb = build_exam_message_and_keyboard(exam_doc)
            await app.bot.send_message(
                chat_id=tg_id,
                text=text,
                parse_mode="HTML",
                reply_markup=kb,
                disable_web_page_preview=True,
            )

            users_col.update_one(
                {"tg_id": tg_id},
                {
                    "$addToSet": {"notified_exam_ids": ex_id},
                    "$set": {"last_notified_at": datetime.utcnow()},
                },
            )

        except Forbidden:
            # User ne bot block kar diya
            block_user(tg_id, reason="blocked_during_new_exam_notify")
        except Exception:
            # baaki errors ko ignore, logs scheduler me aa jayenge
            continue
