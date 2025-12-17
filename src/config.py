
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Local development ke liye .env support
load_dotenv()


@dataclass
class Config:
    # Telegram Bot
    bot_token: str = field(default_factory=lambda: os.environ["BOT_TOKEN"])

    # MongoDB Atlas
    mongo_uri: str = field(default_factory=lambda: os.environ["MONGO_URI"])
    mongo_db_name: str = field(
        default_factory=lambda: os.getenv("MONGO_DB_NAME", "serena_exam_pulse")
    )

    # Optional: future Pyrogram / MTProto use ke liye
    api_id: int = field(
        default_factory=lambda: int(os.getenv("API_ID", "0"))
    )
    api_hash: str = field(
        default_factory=lambda: os.getenv("API_HASH", "")
    )

    # Admin IDs (comma separated)
    admin_ids: list[int] = field(
        default_factory=lambda: [
            int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
        ]
    )

    # Logs ke liye channel/group ID (negative ID for channel)
    log_channel_id: int = field(
        default_factory=lambda: int(os.getenv("LOG_CHANNEL_ID", "0"))
    )

    # Owner contact (username without @)
    owner_username: str = field(
        default_factory=lambda: os.getenv("OWNER_USERNAME", "technicalserena")
    )

    # Official main channel link (Serena Channel)
    channel_link: str = field(
        default_factory=lambda: os.getenv(
            "CHANNEL_LINK",
            "https://t.me/serenaunzipbot",  # default
        )
    )

    # Force Subscribe channel (username ya numeric ID)
    force_sub_channel: str = field(
        default_factory=lambda: os.getenv("FORCE_SUB_CHANNEL", "@serenaunzipbot")
    )

    # EXAM / JOB FEED CHANNEL (tumhara apna channel jahan tum notifications daaloge)
    # Example: -1001234567890
    exam_feed_channel_id: int = field(
        default_factory=lambda: int(os.getenv("EXAM_FEED_CHANNEL_ID", "0"))
    )


config = Config()
