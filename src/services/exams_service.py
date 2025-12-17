from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re

from telegram import Message, InlineKeyboardButton, InlineKeyboardMarkup

from ..database import get_exams_collection

exams_col = get_exams_collection()


def _parse_age_range(line: str) -> tuple[Optional[int], Optional[int]]:
    """
    Age line se min-max age nikalne ki koshish:
    Example formats:
      Age: 18-32
      Age: 18 to 32
      Min 18 Max 32
    """
    nums = re.findall(r"\d{1,2}", line)
    if not nums:
        return None, None
    if len(nums) == 1:
        val = int(nums[0])
        return val, None
    return int(nums[0]), int(nums[1])


def _auto_keywords_from_text(text_lower: str) -> list[str]:
    """
    Agar 'Keywords:' line nahi hai to basic auto keywords generate karo.
    Ye sirf matching me help ke liye hai, magic nahi hai.
    """
    kws: list[str] = []

    if "12th" in text_lower or "10+2" in text_lower or "intermediate" in text_lower:
        kws.extend(["12th", "10+2", "intermediate", "higher secondary"])

    if "graduate" in text_lower or "graduation" in text_lower:
        kws.extend(["graduate", "graduation", "bachelor"])

    for key in ("b.tech", "b.e", "bca", "mca", "b.sc", "bsc", "b.com", "bcom"):
        if key in text_lower:
            kws.append(key)

    if "diploma" in text_lower:
        kws.append("diploma")

    if "iti" in text_lower:
        kws.append("iti")

    # unique
    return sorted(set(kws))


def _parse_exam_text(text: str) -> Dict[str, Any]:
    """
    Channel message text ko parse karke standard fields banata hai.
    Agar kuch field nahi mile to auto-complete / default use hote hain.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = lines[0] if lines else "Untitled Exam / Job"

    result: Dict[str, Any] = {
        "title": title,
        "type": None,  # "Govt Exam" / "Job"
        "org": None,
        "salary": None,
        "notification_date": None,
        "form_start": None,
        "form_end": None,
        "min_age": None,
        "max_age": None,
        "apply_link": None,
        "source_link": None,
        "keywords": [],
        "states": [],
    }

    text_lower = text.lower()

    for line in lines[1:]:
        low = line.lower()

        if low.startswith("type:"):
            result["type"] = line.split(":", 1)[1].strip()
        elif low.startswith("org:") or low.startswith("organisation:") or low.startswith("organization:"):
            result["org"] = line.split(":", 1)[1].strip()
        elif low.startswith("salary:"):
            result["salary"] = line.split(":", 1)[1].strip()
        elif low.startswith("notification:"):
            result["notification_date"] = line.split(":", 1)[1].strip()
        elif low.startswith("start:"):
            result["form_start"] = line.split(":", 1)[1].strip()
        elif low.startswith("end:") or "last date" in low:
            # "End:" ya "Last Date:" line
            parts = line.split(":", 1)
            result["form_end"] = parts[1].strip() if len(parts) > 1 else line.strip()
        elif low.startswith("age:") or "age limit" in low:
            mn, mx = _parse_age_range(line)
            if mn is not None:
                result["min_age"] = mn
            if mx is not None:
                result["max_age"] = mx
        elif low.startswith(("keywords:", "qualification:", "qual:")):
            part = line.split(":", 1)[1].strip() if ":" in line else ""
            # comma ya slash se split
            raw_kws = re.split(r"[,/]", part)
            kws = [kw.strip().lower() for kw in raw_kws if kw.strip()]
            result["keywords"].extend(kws)
        elif low.startswith("apply:"):
            result["apply_link"] = line.split(":", 1)[1].strip()
        elif low.startswith(("source:", "link:", "notification link:", "official:")):
            result["source_link"] = line.split(":", 1)[1].strip()
        elif low.startswith("states:") or low.startswith("state:"):
            states_part = line.split(":", 1)[1].strip() if ":" in line else ""
            st_list = [s.strip() for s in states_part.split(",") if s.strip()]
            result["states"].extend(st_list)

    # Auto-type detection
    if not result["type"]:
        if any(k in text_lower for k in ("ssc", "upsc", "rrb", "railway", "ibps", "psc", "police", "army", "navy", "air force")):
            result["type"] = "Govt Exam"
        else:
            result["type"] = "Job"

    # Org auto: agar missing ho to title ke first words use kar lo
    if not result["org"]:
        # title ke pehle 3-4 shabdon ko org maan lo
        org_guess = " ".join(title.split()[:4])
        result["org"] = org_guess or "Not specified"

    # Keywords auto-complete
    auto_kws = _auto_keywords_from_text(text_lower)
    result["keywords"].extend(auto_kws)
    # unique
    result["keywords"] = sorted(set([k.lower() for k in result["keywords"]]))

    return result


def ingest_exam_from_channel_message(message: Message) -> Dict[str, Any]:
    """
    Tumhare exam channel me se new message ko 'exams' collection me save karta hai.
    """
    text = message.text or message.caption or ""
    if not text.strip():
        return {}

    parsed = _parse_exam_text(text)
    exam_id = f"{message.chat.id}_{message.message_id}"
    now = datetime.utcnow()

    doc: Dict[str, Any] = {
        "exam_id": exam_id,
        "channel_id": message.chat.id,
        "channel_message_id": message.message_id,
        "raw_text": text,
        "created_at": now,
        "active": True,
        **parsed,
    }

    exams_col.update_one(
        {"exam_id": exam_id},
        {"$set": doc},
        upsert=True,
    )

    return doc


def get_recent_exams(days: int = 30) -> List[Dict[str, Any]]:
    """Last N days ke active exams."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    cursor = exams_col.find(
        {
            "created_at": {"$gte": cutoff},
            "active": True,
        }
    ).sort("created_at", -1)
    return list(cursor)


def is_user_eligible_for_exam(user_doc: Dict[str, Any], exam: Dict[str, Any]) -> bool:
    """
    Basic eligibility:
    - Age range
    - Notification preferences (Govt Exam / Job)
    - Qualification keywords
    - State (agar exam limited states ke liye hai)
    """
    age = user_doc.get("age")
    state = (user_doc.get("state") or "").lower()
    quals = user_doc.get("qualifications", [])
    quals_text = " ".join(q.get("text", "") for q in quals).lower()
    prefs = user_doc.get("notification_prefs", {})
    enabled = prefs.get("enabled", True)
    govt_on = prefs.get("govt_exams", True)
    jobs_on = prefs.get("jobs", True)

    if not enabled:
        return False

    ex_type = exam.get("type") or ""
    if ex_type.lower().startswith("govt") and not govt_on:
        return False
    if ex_type.lower().startswith("job") and not jobs_on:
        return False

    # Age check
    if age is not None:
        mn = exam.get("min_age")
        mx = exam.get("max_age")
        if mn is not None and age < mn:
            return False
        if mx is not None and age > mx:
            return False

    # Keywords / qualification
    keywords = [k.lower() for k in exam.get("keywords") or []]
    if keywords:
        if not any(k in quals_text for k in keywords):
            # Agar user ki qualifications me keyword nahi mila to skip
            return False

    # State filter
    ex_states = [s.lower() for s in (exam.get("states") or [])]
    if ex_states and state:
        if state not in ex_states:
            return False

    return True


def get_eligible_exams_for_user(user_doc: Dict[str, Any], days: int = 30) -> List[Dict[str, Any]]:
    """Recent exams me se user ke liye eligible list."""
    exams = get_recent_exams(days=days)
    return [ex for ex in exams if is_user_eligible_for_exam(user_doc, ex)]


def build_exam_message_and_keyboard(exam: Dict[str, Any]) -> tuple[str, Optional[InlineKeyboardMarkup]]:
    """
    Exam / job ke liye pretty message + inline keyboard.
    Ye /jobs aur scheduler, dono ke liye reuse hoga.
    """
    title = exam.get("title") or "Exam / Job"
    ex_type = exam.get("type") or "N/A"
    org = exam.get("org") or "N/A"
    salary = exam.get("salary")
    notif_date = exam.get("notification_date")
    form_start = exam.get("form_start")
    form_end = exam.get("form_end")
    min_age = exam.get("min_age")
    max_age = exam.get("max_age")
    details = exam.get("details") or exam.get("raw_text")

    lines = [
        f"📢 <b>{title}</b>",
        f"🏛 <b>Type:</b> {ex_type}   |   🏢 <b>Org:</b> {org}",
    ]

    if salary:
        lines.append(f"💰 <b>Salary:</b> {salary}")

    if notif_date:
        lines.append(f"📅 <b>Notification:</b> {notif_date}")

    if form_start or form_end:
        form_parts = []
        if form_start:
            form_parts.append(f"Start: {form_start}")
        if form_end:
            form_parts.append(f"Last Date: {form_end}")
        lines.append("📝 <b>Form Dates:</b> " + " | ".join(form_parts))

    if min_age is not None or max_age is not None:
        age_parts = []
        if min_age is not None:
            age_parts.append(f"Min {min_age}")
        if max_age is not None:
            age_parts.append(f"Max {max_age}")
        lines.append("🎯 <b>Age Limit:</b> " + " | ".join(age_parts))

    if details:
        lines.append("")
        lines.append(details)

    text = "\n".join(lines)

    buttons_row = []
    apply_link = (exam.get("apply_link") or "").strip()
    source_link = (exam.get("source_link") or "").strip()

    if apply_link:
        buttons_row.append(
            InlineKeyboardButton(
                "🔗 Apply Now",
                url=apply_link,
            )
        )

    # Source link: jahan se tumne notification li hai (official / channel post link)
    if source_link:
        buttons_row.append(
            InlineKeyboardButton(
                "📄 Official Notification",
                url=source_link,
            )
        )
    else:
        # Agar source_link nahi diya, to kam se kam channel post link de sakte ho:
        # https://t.me/c/<abs(channel_id) without -100> / <message_id>
        chan_id = exam.get("channel_id")
        msg_id = exam.get("channel_message_id")
        if isinstance(chan_id, int) and str(chan_id).startswith("-100") and msg_id:
            post_id = str(chan_id)[4:]
            t_link = f"https://t.me/c/{post_id}/{msg_id}"
            buttons_row.append(
                InlineKeyboardButton(
                    "📄 Channel Post",
                    url=t_link,
                )
            )

    kb = InlineKeyboardMarkup([buttons_row]) if buttons_row else None
    return text, kb
