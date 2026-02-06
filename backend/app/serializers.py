from typing import Dict, Any
from app.schemas import JournalEntry, Summary

def serialize_entry(entry: Dict[str, Any]) -> JournalEntry:
    return JournalEntry(
        id=str(entry["_id"]),
        title=entry["title"],
        content=entry["content"],
        created_at=entry["created_at"],
        updated_at=entry["updated_at"],
    )


def serialize_summary(doc: Dict[str, Any]) -> Summary:
    return Summary(
        id=str(doc["_id"]),
        period=doc["period"],
        start_date=doc["start_date"],
        end_date=doc["end_date"],
        summary=doc["summary"],
        created_at=doc["created_at"],
    )
