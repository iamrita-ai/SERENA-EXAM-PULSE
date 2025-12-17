from datetime import datetime
from typing import Optional, Dict, Any, List
from ..database import get_users_collection, get_blocked_collection

users_col = get_users_collection()
blocked_col = get_blocked_collection()

DEFAULT_NOTIFICATION_PREFS = {
    "enabled": True,
    "govt_exams": True,
    "jobs": True,
    "min_salary": None,
}


def _ensure_notification_prefs(doc: dict) -> dict:
    prefs = doc.get("notification_prefs") or {}
    merged = {**DEFAULT_NOTIFICATION_PREFS, **prefs}
    doc["notification_prefs"] = merged
    return doc


def get_user_by_tg_id(tg_id: int) -> Optional[Dict[str, Any]]:
    doc = users_col.find_one({"tg_id": tg_id})
    if doc:
        doc = _ensure_notification_prefs(doc)
    return doc


def upsert_user_profile(tg_user, profile_data: dict) -> dict:
    now = datetime.utcnow()

    quals: List[dict] = [
        {"text": q} for q in profile_data.get("qualifications", [])
    ]

    update = {
        "$set": {
            "tg_id": tg_user.id,
            "username": tg_user.username,
            "first_name": tg_user.first_name,
            "full_name": profile_data["name"],
            "state": profile_data["state"],
            "category": profile_data["category"],
            "age": profile_data["age"],
            "qualifications": quals,
            "extra_details": profile_data.get("extra_details", ""),
            "updated_at": now,
        },
        "$setOnInsert": {
            "created_at": now,
            "notification_prefs": DEFAULT_NOTIFICATION_PREFS,
            "notified_exam_ids": [],
        },
    }

    users_col.update_one({"tg_id": tg_user.id}, update, upsert=True)
    doc = get_user_by_tg_id(tg_user.id)
    return doc


def delete_user_profile(tg_id: int) -> int:
    res = users_col.delete_one({"tg_id": tg_id})
    return res.deleted_count


def get_user_stats() -> dict:
    total_users = users_col.count_documents({})
    blocked_users = blocked_col.count_documents({})
    return {"total": total_users, "blocked": blocked_users}


def list_users(limit: int = 50) -> list[dict]:
    cursor = users_col.find({}, {"tg_id": 1, "username": 1, "full_name": 1}).sort(
        "created_at", 1
    )
    return list(cursor.limit(limit))


def is_blocked(tg_id: int) -> bool:
    return blocked_col.find_one({"tg_id": tg_id}) is not None


def block_user(tg_id: int, reason: str = "blocked_by_bot") -> None:
    if is_blocked(tg_id):
        return
    blocked_col.insert_one(
        {
            "tg_id": tg_id,
            "reason": reason,
            "blocked_at": datetime.utcnow(),
        }
    )


def unblock_user(tg_id: int) -> None:
    blocked_col.delete_one({"tg_id": tg_id})


def get_all_active_users_cursor():
    """All users who are not blocked."""
    blocked_ids = [b["tg_id"] for b in blocked_col.find({}, {"tg_id": 1})]
    query = {}
    if blocked_ids:
        query = {"tg_id": {"$nin": blocked_ids}}
    return users_col.find(query)
