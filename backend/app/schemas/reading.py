"""Reading schemas."""
from pydantic import BaseModel
from datetime import datetime


class ReadingProgressOut(BaseModel):
    id: int
    book_id: int
    current_page: int
    total_pages: int | None = None
    progress_percent: float
    status: str
    total_read_time: int
    last_read_at: datetime | None = None
    epub_cfi: str | None = None

    model_config = {"from_attributes": True}


class ReadingProgressUpdate(BaseModel):
    current_page: int | None = None
    total_pages: int | None = None
    epub_cfi: str | None = None


class ReadingStatsOut(BaseModel):
    total_read_time_seconds: int
    total_read_time_hours: float
    books_completed: int
    books_reading: int
