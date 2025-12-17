from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from .config import config
from .services.logging_service import setup_logging
from .handlers.start import start_command
from .handlers.help import help_command
from .handlers.profile import profile_view_command, PROFILE_CONV_HANDLER
from .handlers.settings import settings_command, settings_callback
from .handlers.admin import status_command, users_command, broadcast_command
from .handlers.jobs import jobs_command
from .handlers.feed import exam_channel_post_handler
from .services.scheduler import setup_scheduled_jobs


def main():
    # Logging
    setup_logging()

    # Application (PTB 20/21 style)
    application = Application.builder().token(config.bot_token).build()

    # ---------------- Handlers ---------------- #

    # 1) Tumhare EXAM_FEED_CHANNEL ke liye handler:
    # Sirf channel_post updates handle karega (users ke chats nahi)
    application.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            exam_channel_post_handler,
        )
    )

    # 2) User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_view_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # 3) Jobs / Govt Exams list (current eligibility)
    application.add_handler(CommandHandler(["jobs", "job"], jobs_command))

    # 4) Profile conversation (create/edit)
    application.add_handler(PROFILE_CONV_HANDLER)

    # 5) Settings inline callbacks
    application.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern="^(toggle_notif:|settings_delete_profile)$",
        )
    )

    # 6) Admin commands
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    # 7) Scheduler jobs (hourly/daily)
    setup_scheduled_jobs(application)

    # ---------------- Long Polling ---------------- #

    # Long polling se bot Telegram se updates le raha hoga.
    # Background Worker ke liye ye best hai.
    application.run_polling(
        # Agar channel_post ke updates bhi chahiye:
        allowed_updates=["message", "callback_query", "channel_post"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
