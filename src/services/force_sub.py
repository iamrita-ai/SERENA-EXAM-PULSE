from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from telegram.error import Forbidden, BadRequest

from ..config import config


async def ensure_subscribed(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    True  -> user ne required channel join kiya hua hai
    False -> user ko join karne ka message bhej diya, baaki handler ko aage mat chalao
    """
    channel = config.force_sub_channel
    if not channel:
        # Agar FORCE_SUB_CHANNEL set nahi kiya hua to force-sub disable
        return True

    user = update.effective_user
    bot = context.bot

    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user.id)

        # PTB 20/21 versions me statuses ka naam change ho sakta hai.
        # Hum LEFT + (KICKED ya BANNED jo bhi available ho) ko "not joined" manenge.
        bad_statuses = {ChatMemberStatus.LEFT}
        if hasattr(ChatMemberStatus, "KICKED"):
            bad_statuses.add(ChatMemberStatus.KICKED)
        if hasattr(ChatMemberStatus, "BANNED"):
            bad_statuses.add(ChatMemberStatus.BANNED)

        if member.status in bad_statuses:
            raise Forbidden("user not joined")

        # Member / admin / owner etc. -> allowed
        return True

    except (Forbidden, BadRequest):
        # Channel join link
        # Agar CHANNEL_LINK env me diya hai to woh use hoga, warna username se banayenge
        link = config.channel_link or f"https://t.me/{str(channel).lstrip('@')}"

        text = (
            "⚠️ Pehle hamara official channel join karna zaroori hai.\n\n"
            "✅ Channel join karne ke baad /start dubara type karein."
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Serena Channel",
                        url=link,
                    )
                ]
            ]
        )

        # message / callback dono case handle karein
        if update.effective_message:
            await update.effective_message.reply_text(
                text,
                reply_markup=keyboard,
            )
        else:
            await bot.send_message(
                chat_id=user.id,
                text=text,
                reply_markup=keyboard,
            )

        return False
