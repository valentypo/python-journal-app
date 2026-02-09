import hashlib
from datetime import date, timedelta
from typing import List

def build_journal_text(entries):
    text = ""
    for i, entry in enumerate(entries, start=1):
        text += f"""
        Entry {i}
        Title: {entry['title']}
        Content: {entry['content']}
        """
    return text


def get_date_range(period: str):
    today = date.today()

    if period == "daily":
        start = today
        end = today

    elif period == "weekly":
        start = today - timedelta(days=7)
        end = today

    elif period == "monthly":
        start = today.replace(day=1)
        end = today

    else:
        raise ValueError("Invalid period")

    return (
        f"{start.isoformat()}T00:00:00",
        f"{end.isoformat()}T23:59:59",
    )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for embeddings.
    """
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start = end - overlap

    return chunks


def hash_text(text: str) -> str:
    """
    Create stable deterministic ID for text chunks.
    """
    return hashlib.sha256(text.encode()).hexdigest()


def merge_chunks(chunks: List[str]) -> str:
    """
    Merge retrieved chunks into one context block for LLM.
    """
    return "\n\n".join(chunks)
