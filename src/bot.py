import os
import threading
import http.server
import socketserver
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChannelPostHandler,
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


logger = logging.getLogger(__name__)


def start_health_http_server():
    """
    Render ke Web Service ko ek HTTP port open chahiye.
    Ye lightweight HTTP server sirf health check ke liye chalaya jaa raha hai.
    Bot Telegram se long-polling se updates lega.
    """
    port = int(os.getenv("PORT", "8000"))

    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        # Logging ko thoda clean rakhne ke liye override
        def log_message(self, format, *args):
            logger.info("Health HTTP: " + format % args)

        def do_GET(self):
            # Simple 200 OK response for any path (/, /health, etc.)
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")

    try:
        with socketserver.TCPServer(("", port), HealthHandler) as httpd:
            logger.info("Health HTTP server running on port %s", port)
            httpd.serve_forever()
    except OSError as e:
        logger.error("Failed to start health HTTP server on port %s: %s", port, e)


def main():
    # Logging setup
    setup_logging()

    # Health HTTP server ko ek alag thread me start karo
    health_thread = threading.Thread(target=start_health_http_server, daemon=True)
    health_thread.start()

    # Telegram Application (PTB 20/21 style)
    application = Application.builder().token(config.bot_token).build()

    # ---------------- Handlers ---------------- #

    # 1) Tumhare EXAM_FEED_CHANNEL ke liye handler:
    # Sirf channel_post updates handle karega (users ke chats ko affect nahi karega)
    application.add_handler(
        ChannelPostHandler(exam_channel_post_handler)
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

    # ---------------- Long Polling (no webhook) ---------------- #

    # Long polling se bot Telegram se updates lega.
    # Render ka Web Service health check upar wale HTTP server se satisfy ho jayega.
    application.run_polling(
        allowed_updates=["message", "callback_query", "channel_post"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
