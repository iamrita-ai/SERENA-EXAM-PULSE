from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..config import config


def get_start_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("📢 Serena Channel", url=config.channel_link),
            InlineKeyboardButton(
                "👤 Owner Contact", url=f"https://t.me/{config.owner_username}"
            ),
        ],
        [
            InlineKeyboardButton("📝 Create / Edit Profile", callback_data="create_profile")
        ],
    ]
    return InlineKeyboardMarkup(buttons)
