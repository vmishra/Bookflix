"""Feed schemas."""
from pydantic import BaseModel
from datetime import datetime


class FeedItemOut(BaseModel):
    id: int
    item_type: str
    title: str
    content: str
    book_ids: list[int] = []
    metadata_json: dict = {}
    is_read: bool
    is_pinned: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedItemUpdate(BaseModel):
    is_read: bool | None = None
    is_pinned: bool | None = None


class FeedResponse(BaseModel):
    items: list[FeedItemOut]
    total: int
    unread_count: int
