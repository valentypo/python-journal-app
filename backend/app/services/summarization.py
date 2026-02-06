from datetime import datetime
from openai import OpenAI
from app.utils import build_journal_text
from pymongo import MongoClient
import os

# Use a standalone MongoClient inside tasks so Celery workers don't
# depend on Flask's `current_app` application context.
_MONGO_URI = os.getenv("MONGODB_URI")
if not _MONGO_URI:
    raise RuntimeError("MONGODB_URI not found in environment for summarization task")
_client = MongoClient(_MONGO_URI)
_db = _client["journal_db"]

def summarize_entries(entries, period: str) -> str:
    journal_text = build_journal_text(entries)
    client = OpenAI()

    system_prompt = f"""
    The text you received is user's journal.
    Summarize the journal for a {period} period.
    1–3 sentences,warm and concise.
    If content is weak, gently suggest improvement.
    """

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": journal_text},
        ],
    )

    return response.output_text


def summarize_and_store(period: str, start: str, end: str):
    entries = list(
        _db.entries.find({
            "created_at": {"$gte": start, "$lte": end}
        })
    )

    if not entries:
        return None

    existing = _db.summaries.find_one({
        "period": period,
        "start_date": start,
        "end_date": end,
    })

    if existing:
        return existing["summary"]

    summary = summarize_entries(entries, period)

    _db.summaries.insert_one({
        "period": period,
        "start_date": start,
        "end_date": end,
        "summary": summary,
        "created_at": datetime.now().isoformat(),
    })

    return summary