import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str = field(default_factory=lambda: os.environ["BOT_TOKEN"])
    mongo_uri: str = field(default_factory=lambda: os.environ["MONGO_URI"])
    mongo_db_name: str = field(default_factory=lambda: os.environ.get("MONGO_DB_NAME", "serena_exam_pulse"))
    admin_ids: list[int] = field(
        default_factory=lambda: [
            int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
        ]
    )
    log_channel_id: int = field(
        default_factory=lambda: int(os.getenv("LOG_CHANNEL_ID", "0"))
    )
    owner_username: str = field(
        default_factory=lambda: os.getenv("OWNER_USERNAME", "technicalserena")
    )
    channel_link: str = field(
        default_factory=lambda: os.getenv("CHANNEL_LINK", "https://t.me/serenaunzipbot")
    )


config = Config()
