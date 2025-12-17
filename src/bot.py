import os

from telegram.ext import (
    Application,
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
from .handlers.jobs import jobs_command
from .services.scheduler import setup_scheduled_jobs


def main():
    # Logging
    setup_logging()

    # Application (PTB 20/21 style)
    application = Application.builder().token(config.bot_token).build()

    # ---------------- Handlers ---------------- #

    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_view_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Jobs / Govt Exams list (current eligibility)
    application.add_handler(CommandHandler(["jobs", "job"], jobs_command))

    # Profile conversation (create/edit)
    application.add_handler(PROFILE_CONV_HANDLER)

    # Settings inline callbacks
    application.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern="^(toggle_notif:|settings_delete_profile)$",
        )
    )

    # Admin commands
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    # Scheduler jobs (hourly/daily)
    setup_scheduled_jobs(application)

    # ---------------- Webhook Config for Render ---------------- #

    # Render automatically PORT env var set karta hai
    port = int(os.getenv("PORT", "8000"))

    # Render external URL, e.g. https://serena-exam-pulse.onrender.com
    external_url = os.getenv("RENDER_EXTERNAL_URL")

    # Secret path for webhook
    webhook_path = os.getenv("WEBHOOK_PATH", f"/webhook/{config.bot_token}")

    if external_url:
        webhook_url = external_url.rstrip("/") + webhook_path
    else:
        # Fallback: agar kisi reason se RENDER_EXTERNAL_URL nahi mila
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            raise RuntimeError(
                "WEBHOOK_URL ya RENDER_EXTERNAL_URL env variable set karo "
                "taaki webhook URL generate ho sake."
            )

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path.lstrip("/"),
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
