from pydantic import BaseModel
from typing import Optional, Literal


class JournalEntryCreate(BaseModel):
    title: str
    content: str


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class JournalEntry(BaseModel):
    id: str
    title: str
    content: str
    created_at: str
    updated_at: str


class Summary(BaseModel):
    id: str
    period: Literal["daily", "weekly", "monthly"]
    start_date: str
    end_date: str
    summary: str
    created_at: str


class SummaryCreate(BaseModel):
    period: Literal["daily", "weekly", "monthly"]
    start_date: str
    end_date: str
    summary: str
