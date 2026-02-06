from datetime import datetime
from openai import OpenAI
from app.utils import build_journal_text
from flask import current_app

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
        current_app.db.entries.find({
            "created_at": {"$gte": start, "$lte": end}
        })
    )

    if not entries:
        return None

    existing = current_app.db.summaries.find_one({
        "period": period,
        "start_date": start,
        "end_date": end,
    })

    if existing:
        return existing["summary"]

    summary = summarize_entries(entries, period)

    current_app.db.summaries.insert_one({
        "period": period,
        "start_date": start,
        "end_date": end,
        "summary": summary,
        "created_at": datetime.now().isoformat(),
    })

    return summary