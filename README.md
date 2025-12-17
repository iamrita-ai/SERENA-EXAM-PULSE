# Serena Exam Pulse – Telegram Bot

Personalized exam & job alerts Telegram bot.

**Features**

- User profile creation:
  - Name, State, Category, Age
  - Multiple Qualifications
  - Extra/custom details
- Eligibility-based:
  - Govt Exams
  - New Job Posts
  - Salary & criteria overview
  - Apply links as inline buttons
- Auto notifications (hourly/daily scheduler)
- Admin panel:
  - `/status` – stats
  - `/users` – list users
  - `/broadcast` – send message to all

## Tech Stack

- Python 3.10+
- [python-telegram-bot v20+](https://python-telegram-bot.org/)
- MongoDB Atlas (cloud)
- JobQueue scheduler (built into PTB)

## Setup

1. Clone repo

```bash
git clone https://github.com/yourusername/serena-exam-pulse-bot.git
cd serena-exam-pulse-bot

2. Create virtualenv & install deps
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Configure environment
Copy .env.example to .env
Fill values:

BOT_TOKEN=123456:ABC-Your-Telegram-Bot-Token
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=serena_exam_pulse

ADMIN_IDS=123456789,987654321
LOG_CHANNEL_ID=-1001234567890

OWNER_USERNAME=technicalserena
CHANNEL_LINK=https://t.me/serenaunzipbot

Run bot

python -m src.bot


Main Commands
User:

/start – welcome + buttons (Serena Channel, Owner Contact, Create/Edit Profile)
/help – usage
/profile – show saved profile
/editprofile – create/update profile wizard
/settings – notification & profile settings
Admin:

/status – total users + blocked users
/users – list of users (first 50)
/broadcast <message> – send message to all users
Note
Exam/job matching currently uses sample data in services/exams_service.py.
You can plug your own scraper/API inside get_eligible_exams_for_user.
text


---

## 3. `requirements.txt`

```txt
python-telegram-bot==20.7
pymongo[srv]==4.6.1
python-dotenv==1.0.1



BOT_TOKEN=123456789:ABCDEF-your-telegram-token
MONGO_URI=mongodb+srv://user:pass@cluster0.xxxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=serena_exam_pulse

# Comma separated telegram user IDs (admins)
ADMIN_IDS=123456789,987654321

# Channel/group ID for profile logs (negative for channels)
LOG_CHANNEL_ID=-1001234567890

OWNER_USERNAME=technicalserena
CHANNEL_LINK=https://t.me/serenaunzipbot
