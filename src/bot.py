from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)
from .config import config
from .services.logging_service import setup_logging
from .handlers.start import start_command
from .handlers.help import help_command
from .handlers.profile import profile_view_command, PROFILE_CONV_HANDLER
from .handlers.settings import settings_command, settings_callback
from .handlers.admin import status_command, users_command, broadcast_command
from .services.scheduler import setup_scheduled_jobs


def main():
    setup_logging()

    application = ApplicationBuilder().token(config.bot_token).build()

    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_view_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Profile conversation (create/edit)
    application.add_handler(PROFILE_CONV_HANDLER)

    # Settings callbacks (inline buttons)
    application.add_handler(
        CallbackQueryHandler(settings_callback, pattern="^(toggle_notif:|settings_delete_profile)")
    )

    # Admin commands
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    # Scheduler jobs
    setup_scheduled_jobs(application)

    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
