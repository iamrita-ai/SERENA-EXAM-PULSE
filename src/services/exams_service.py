from typing import List, Dict, Any

# TODO: Integrate real exam/job scraper or API here.

SAMPLE_EXAMS: List[Dict[str, Any]] = [
    {
        "id": "ssc_cgl_2025",
        "title": "SSC CGL 2025",
        "type": "Govt Exam",
        "org": "Staff Selection Commission",
        "min_age": 18,
        "max_age": 32,
        "required_qualifications_keywords": ["graduation", "bachelor", "b.sc", "b.com", "b.a"],
        "states": [],
        "salary": "Approx ₹50,000 - ₹1,50,000 per month",
        "apply_link": "https://ssc.nic.in/",
        "details": "All India graduate level exam for various Group B & C posts.",
    },
    {
        "id": "ibps_po_2025",
        "title": "IBPS PO 2025",
        "type": "Govt Exam",
        "org": "IBPS",
        "min_age": 20,
        "max_age": 30,
        "required_qualifications_keywords": ["graduation", "bachelor"],
        "states": [],
        "salary": "Approx ₹45,000 - ₹70,000 per month",
        "apply_link": "https://ibps.in/",
        "details": "Probationary Officer recruitment in public sector banks.",
    },
    {
        "id": "junior_developer_private",
        "title": "Junior Python Developer",
        "type": "Job",
        "org": "Private IT Firm",
        "min_age": 18,
        "max_age": 30,
        "required_qualifications_keywords": ["b.tech", "bca", "mca", "b.sc cs", "python"],
        "states": ["karnataka", "maharashtra", "delhi"],
        "salary": "₹3 LPA - ₹6 LPA",
        "apply_link": "https://example.com/apply/python-dev",
        "details": "Entry-level Python developer role. Good for freshers.",
    },
]


def get_eligible_exams_for_user(user_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    VERY SIMPLE rule-based filter on SAMPLE_EXAMS.
    Replace with real logic / scraped data in production.
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
        return []

    eligible: List[Dict[str, Any]] = []

    for exam in SAMPLE_EXAMS:
        if age is not None:
            if exam.get("min_age") and age < exam["min_age"]:
                continue
            if exam.get("max_age") and age > exam["max_age"]:
                continue

        if exam["type"] == "Govt Exam" and not govt_on:
            continue
        if exam["type"] == "Job" and not jobs_on:
            continue

        kw = exam.get("required_qualifications_keywords") or []
        if kw and not any(k in quals_text for k in kw):
            continue

        states = [s.lower() for s in exam.get("states") or []]
        if states and state and state not in states:
            continue

        eligible.append(exam)

    return eligible
