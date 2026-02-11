from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


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


class RAGQuerySchema(BaseModel):
    query: str = Field(..., description="User question")
    top_k: int = Field(default=5, description="How many chunks to retrieve")


class RAGSourceSchema(BaseModel):
    journal_id: str
    date: str


class RAGResponseSchema(BaseModel):
    query: str
    answer: str
    sources: List[RAGSourceSchema]
    created_at: str