from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any


def get_settings_keyboard(user_doc: Dict[str, Any]) -> InlineKeyboardMarkup:
    prefs = user_doc.get("notification_prefs", {})
    enabled = prefs.get("enabled", True)
    govt = prefs.get("govt_exams", True)
    jobs = prefs.get("jobs", True)

    buttons = [
        [
            InlineKeyboardButton(
                f"🔔 Notifications: {'ON' if enabled else 'OFF'}",
                callback_data="toggle_notif:enabled",
            )
        ],
        [
            InlineKeyboardButton(
                f"🏛 Govt Exams: {'ON' if govt else 'OFF'}",
                callback_data="toggle_notif:govt_exams",
            )
        ],
        [
            InlineKeyboardButton(
                f"💼 Jobs: {'ON' if jobs else 'OFF'}",
                callback_data="toggle_notif:jobs",
            )
        ],
        [
            InlineKeyboardButton("✏️ Edit Profile", callback_data="settings_edit_profile")
        ],
        [
            InlineKeyboardButton(
                "🗑 Delete Profile", callback_data="settings_delete_profile"
            )
        ],
    ]
    return InlineKeyboardMarkup(buttons)
