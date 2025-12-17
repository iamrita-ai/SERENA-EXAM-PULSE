from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..config import config


def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    /start pe dikhne wala main inline keyboard.
    - Serena Channel
    - Owner Contact
    - Create / Edit Profile
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="📢 Serena Channel",
                url=config.channel_link,
            ),
            InlineKeyboardButton(
                text="👤 Owner Contact",
                url=f"https://t.me/{config.owner_username}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📝 Create / Edit Profile",
                callback_data="create_profile",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
