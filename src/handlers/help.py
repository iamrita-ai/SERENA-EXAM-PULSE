from telegram import Update
from telegram.ext import ContextTypes

from ..models.user import is_blocked


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_blocked(user.id):
        return

    text = (
        "✨ <b>Serena Exam Pulse – Help & Guide</b>\n\n"
        "Ye bot aapki <b>profile</b> ke hisaab se <b>Govt Exams</b> aur "
        "<b>Jobs</b> ki <u>personalized notifications</u> bhejta hai.\n\n"
        "<b>How it works:</b>\n"
        "1️⃣ /editprofile use karke apni exam profile banaiye:\n"
        "   • Name, State, Category, Age\n"
        "   • Multiple Qualifications (degree, year, % – optional)\n"
        "   • Extra details (preferred exams, city, etc.)\n"
        "2️⃣ Bot aapka data analyse karke current Govt Exams & Jobs se match karta hai.\n"
        "3️⃣ Hourly/Daily scheduler se eligibility-based notifications milti rahengi.\n"
        "4️⃣ Kabhi bhi /jobs likh kar abhi ke matching exams/jobs dekh sakte hain.\n\n"
        "<b>User Commands:</b>\n"
        "• /start – Minimal welcome screen + main buttons (Channel, Owner, Profile)\n"
        "• /editprofile – Nayi profile create karein ya purani edit karein (step-by-step wizard)\n"
        "• /profile – Aapki saved exam profile dekhne ke liye\n"
        "• /settings – Notifications (ON/OFF), Govt Exams/Jobs toggles, profile delete\n"
        "• /jobs – Aapki profile ke hisaab se current Govt Exams & Jobs ki list + Apply buttons\n"
        "• /help – Yeh help & introduction message\n\n"
        "<b>Admin Commands:</b>\n"
        "• /status – Total users + blocked users stats\n"
        "• /users – First 50 users ki list\n"
        "• /broadcast &lt;message&gt; – Sab active users ko message bhejna\n\n"
        "⚙️ <i>Note:</i> Real-time exam data ke liye aap code me "
        "<code>services/exams_service.py</code> me apne sources/scrapers add kar sakte hain."
    )

    await update.effective_message.reply_text(text, parse_mode="HTML")
