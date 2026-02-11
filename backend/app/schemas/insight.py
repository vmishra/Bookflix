"""Insight schemas."""
from pydantic import BaseModel
from datetime import datetime


class InsightOut(BaseModel):
    id: int
    book_id: int
    insight_type: str
    title: str
    content: str
    supporting_quote: str | None = None
    importance: int
    refinement_level: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InsightConnectionOut(BaseModel):
    insight_id: int
    book_id: int
    title: str
    content: str
    type: str


class BookInsightsResponse(BaseModel):
    book_id: int
    concepts: list[InsightOut] = []
    frameworks: list[InsightOut] = []
    takeaways: list[InsightOut] = []
