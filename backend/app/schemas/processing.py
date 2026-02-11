"""Processing schemas."""
from pydantic import BaseModel
from datetime import datetime


class ProcessingJobOut(BaseModel):
    id: int
    book_id: int
    stage: str
    status: str
    attempts: int
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ScanRequest(BaseModel):
    directory: str


class ScanResponse(BaseModel):
    task_id: str
    directory: str
    message: str


class LibraryStatsOut(BaseModel):
    total_books: int
    processed_books: int
    pending_books: int
    total_chunks: int
    total_insights: int
