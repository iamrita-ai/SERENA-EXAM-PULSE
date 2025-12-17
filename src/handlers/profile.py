from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from ..models.user import get_user_by_tg_id, upsert_user_profile, is_blocked
from ..services.logging_service import send_profile_log

# Conversation states
ASK_NAME, ASK_STATE, ASK_CATEGORY, ASK_AGE, ASK_QUALIFICATIONS, ASK_EXTRA, CONFIRM_PROFILE = range(7)


async def profile_view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ki saved profile dikhata hai."""
    user = update.effective_user
    if is_blocked(user.id):
        return

    doc = get_user_by_tg_id(user.id)
    if not doc:
        text = (
            "Aapki profile abhi create nahi hui hai.\n"
            "📝 Nayi profile banane ke liye /editprofile ya /start par Create / Edit Profile dabayein."
        )
        await update.effective_message.reply_text(text)
        return

    await update.effective_message.reply_text(
        build_profile_text(doc),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✏️ Edit Profile", callback_data="settings_edit_profile"
                    )
                ]
            ]
        ),
    )


def build_profile_text(user_doc: dict) -> str:
    """User profile ko pretty text me convert kare."""
    lines = [
        "👤 <b>Aapki Exam Profile</b>",
        "",
        f"<b>Name:</b> {user_doc.get('full_name')}",
        f"<b>State:</b> {user_doc.get('state')}",
        f"<b>Category:</b> {user_doc.get('category')}",
        f"<b>Age:</b> {user_doc.get('age')}",
    ]

    quals = user_doc.get("qualifications", [])
    if quals:
        lines.append("<b>Qualifications:</b>")
        for q in quals:
            lines.append(f" • {q.get('text')}")
    else:
        lines.append("<b>Qualifications:</b> N/A")

    extra = user_doc.get("extra_details")
    if extra:
        lines.append("")
        lines.append(f"<b>Extra Details:</b>\n{extra}")

    return "\n".join(lines)


# ---------- Profile Wizard Helpers ----------

def _get_message_from_update(update: Update):
    """Message object nikaal lo chahe /command se aaye ya callback se."""
    if update.message:
        return update.message
    if update.callback_query:
        return update.callback_query.message
    return None


async def start_profile_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Entry point for create/edit profile (via /editprofile command
    ya 'Create / Edit Profile' / 'Edit Profile' button).
    """
    tg_user = update.effective_user
    if is_blocked(tg_user.id):
        return ConversationHandler.END

    msg = _get_message_from_update(update)
    if update.callback_query:
        await update.callback_query.answer()

    # Temporary data store
    context.user_data["profile_wizard"] = {"qualifications": []}

    await msg.reply_text(
        "Chaliye aapki exam profile banate hain.\n\n"
        "1/6 – <b>Aapka full name?</b>",
        parse_mode="HTML",
    )
    return ASK_NAME


async def ask_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["profile_wizard"]["name"] = update.message.text.strip()
    await update.message.reply_text(
        "2/6 – <b>State</b> (jaise: Uttar Pradesh, Maharashtra, Delhi, ...)?",
        parse_mode="HTML",
    )
    return ASK_STATE


async def ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["profile_wizard"]["state"] = update.message.text.strip()
    await update.message.reply_text(
        "3/6 – <b>Category</b> (General / OBC / SC / ST / EWS / etc.)?",
        parse_mode="HTML",
    )
    return ASK_CATEGORY


async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["profile_wizard"]["category"] = update.message.text.strip()
    await update.message.reply_text(
        "4/6 – <b>Age</b> (sirf number likhiye, jaise 23):",
        parse_mode="HTML",
    )
    return ASK_AGE


async def ask_qualifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        age = int(text)
    except ValueError:
        await update.message.reply_text("❌ Kripya valid age (sirf number) likhiye.")
        return ASK_AGE

    context.user_data["profile_wizard"]["age"] = age

    await update.message.reply_text(
        "5/6 – <b>Qualifications</b> likhiye (multiple allowed):\n"
        "Har ek line me ek degree likhiye.\n"
        "Example:\n"
        "• B.Tech CSE 2023\n"
        "• 12th PCM 2019 – 85%\n\n"
        "Jab sab likh lo, 'done' type kar dein.",
        parse_mode="HTML",
    )
    return ASK_QUALIFICATIONS


async def collect_qualification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() in ("done", "ho gya", "ho gaya", "finish", "ho gaya hai"):
        return await ask_extra_details(update, context)

    context.user_data["profile_wizard"]["qualifications"].append(text)
    await update.message.reply_text(
        "Aur qualification add karni hai to likhte rahiye.\n"
        "Jab complete ho jaye to 'done' likh dein."
    )
    return ASK_QUALIFICATIONS


async def ask_extra_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "6/6 – Koi <b>extra details</b> (preparation status, preferred exams, city, etc.)?\n"
        "Agar kuch nahi hai to 'skip' likh dein.",
        parse_mode="HTML",
    )
    return ASK_EXTRA


async def confirm_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() != "skip":
        context.user_data["profile_wizard"]["extra_details"] = text
    else:
        context.user_data["profile_wizard"]["extra_details"] = ""

    profile = context.user_data["profile_wizard"]
    summary = [
        "✅ <b>Please confirm your profile:</b>",
        "",
        f"<b>Name:</b> {profile.get('name')}",
        f"<b>State:</b> {profile.get('state')}",
        f"<b>Category:</b> {profile.get('category')}",
        f"<b>Age:</b> {profile.get('age')}",
    ]
    quals = profile.get("qualifications", [])
    if quals:
        summary.append("<b>Qualifications:</b>")
        for q in quals:
            summary.append(f" • {q}")
    else:
        summary.append("<b>Qualifications:</b> N/A")

    extra = profile.get("extra_details")
    if extra:
        summary.append("")
        summary.append(f"<b>Extra Details:</b>\n{extra}")

    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💾 Save", callback_data="profile_save"),
                InlineKeyboardButton("❌ Cancel", callback_data="profile_cancel"),
            ]
        ]
    )

    await update.message.reply_text(
        "\n".join(summary), parse_mode="HTML", reply_markup=kb
    )
    return CONFIRM_PROFILE


async def handle_profile_confirm_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Inline buttons: Save / Cancel."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "profile_cancel":
        context.user_data.pop("profile_wizard", None)
        await query.edit_message_text("❌ Profile creation/update cancel kar di gayi.")
        return ConversationHandler.END

    if data == "profile_save":
        tg_user = update.effective_user
        profile = context.user_data.get("profile_wizard") or {}
        user_doc = upsert_user_profile(tg_user, profile)

        await query.edit_message_text(
            "✅ Aapki profile save ho gayi.\n\n"
            "Ab bot aapko eligibility-based exams & jobs ki notifications bhejega."
        )

        # Logs channel me resume-style profile bhejo
        await send_profile_log(context.application, user_doc)

        context.user_data.pop("profile_wizard", None)
        return ConversationHandler.END

    return ConversationHandler.END


async def cancel_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback /cancel."""
    context.user_data.pop("profile_wizard", None)
    await update.effective_message.reply_text("❌ Profile wizard cancel kar diya gaya.")
    return ConversationHandler.END


# ConversationHandler object jise bot.py me add kiya gaya hai
PROFILE_CONV_HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler("editprofile", start_profile_wizard),
        CallbackQueryHandler(
            start_profile_wizard,
            pattern="^(create_profile|settings_edit_profile)$",
        ),
    ],
    states={
        ASK_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_state),
        ],
        ASK_STATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_category),
        ],
        ASK_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age),
        ],
        ASK_AGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_qualifications),
        ],
        ASK_QUALIFICATIONS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_qualification),
        ],
        ASK_EXTRA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_profile),
        ],
        CONFIRM_PROFILE: [
            CallbackQueryHandler(
                handle_profile_confirm_callback,
                pattern="^(profile_save|profile_cancel)$",
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_profile),
    ],
    name="profile_wizard",
    persistent=False,
    # per_chat & per_user defaults PTB handle karega,
    # per_message use nahi kar rahe -> warning khatam.
    )
