import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Local development ke liye .env support (Render par env vars se hi kaam hoga)
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

    # Optional: agar future me Pyrogram / MTProto use karna ho
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
        default_factory=lambda: int(os.getenv("LOG_CHANNEL_ID", "-1003286415377"))
    )

    # Owner contact (username without @)
    owner_username: str = field(
        default_factory=lambda: os.getenv("OWNER_USERNAME", "technicalserena")
    )

    # Official main channel link (Serena Channel)
    channel_link: str = field(
        default_factory=lambda: os.getenv(
            "CHANNEL_LINK",
            "https://t.me/serenaunzipbot",  # default tumhara channel
        )
    )

    # Force Subscribe channel (username ya numeric ID)
    # Example: "@serenaunzipbot" ya "-1001234567890"
    force_sub_channel: str = field(
        default_factory=lambda: os.getenv(
            "FORCE_SUB_CHANNEL", "@serenaunzipbot"
        )
    )


config = Config()
