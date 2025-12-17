from telegram import Update
from telegram.ext import ContextTypes
from ..models.user import get_user_by_tg_id, is_blocked, delete_user_profile
from ..keyboards.settings_menu import get_settings_keyboard
from ..database import get_users_collection

users_col = get_users_collection()


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    if is_blocked(tg_user.id):
        return

    doc = get_user_by_tg_id(tg_user.id)
    if not doc:
        await update.effective_message.reply_text(
            "Aapki profile abhi create nahi hui hai.\n"
            "Pehle /editprofile use karke apni profile banaiye."
        )
        return

    await update.effective_message.reply_text(
        "⚙️ <b>Settings</b>\n\n"
        "Yahan se aap notifications aur profile manage kar sakte hain.",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(doc),
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_user = query.from_user

    if is_blocked(tg_user.id):
        return

    data = query.data
    doc = get_user_by_tg_id(tg_user.id)
    if not doc:
        await query.edit_message_text(
            "Profile nahi mili. Pehle /editprofile se profile bna lijiye."
        )
        return

    if data.startswith("toggle_notif:"):
        key = data.split(":", 1)[1]
        prefs = doc.get("notification_prefs", {})
        current = prefs.get(key, True)
        prefs[key] = not current
        users_col.update_one(
            {"tg_id": tg_user.id}, {"$set": {"notification_prefs": prefs}}
        )
        # Refresh
        new_doc = get_user_by_tg_id(tg_user.id)
        await query.edit_message_reply_markup(
            reply_markup=get_settings_keyboard(new_doc)
        )

    elif data == "settings_delete_profile":
        deleted = delete_user_profile(tg_user.id)
        if deleted:
            await query.edit_message_text("🗑 Aapki profile delete kar di gayi.")
        else:
            await query.edit_message_text("Profile pehle se hi exist nahi karti.")
