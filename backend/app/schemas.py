from pydantic import BaseModel
from typing import Optional


class JournalEntryCreate(BaseModel):
    title: str
    content: str


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
