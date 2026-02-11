"""Book schemas."""
from pydantic import BaseModel
from datetime import datetime


class BookFileOut(BaseModel):
    id: int
    file_path: str
    file_type: str
    file_size: int | None = None

    model_config = {"from_attributes": True}


class BookBase(BaseModel):
    title: str
    author: str | None = None
    isbn: str | None = None
    description: str | None = None
    publisher: str | None = None
    published_date: str | None = None
    language: str = "en"


class BookOut(BookBase):
    id: int
    page_count: int | None = None
    file_hash: str
    cover_path: str | None = None
    processing_status: str
    processing_progress: float
    rating: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookDetailOut(BookOut):
    files: list[BookFileOut] = []

    model_config = {"from_attributes": True}


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    description: str | None = None
    publisher: str | None = None
    language: str | None = None


class BookListResponse(BaseModel):
    items: list[BookOut]
    total: int
    skip: int
    limit: int
