"""Chat schemas."""
from pydantic import BaseModel
from datetime import datetime


class ChatSessionCreate(BaseModel):
    title: str = "New Chat"
    book_ids: list[int] = []


class ChatSessionOut(BaseModel):
    id: int
    title: str
    book_ids: list[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    content: str


class SourceChunkOut(BaseModel):
    chunk_id: int
    book_title: str | None = None
    page_number: int | None = None
    snippet: str


class ChatMessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    source_chunks: list[dict] = []
    model_used: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
