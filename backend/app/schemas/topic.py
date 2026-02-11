"""Topic schemas."""
from pydantic import BaseModel
from datetime import datetime


class TopicOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    keywords: list[str] = []
    book_count: int
    color: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TopicGraphNode(BaseModel):
    id: int
    name: str
    book_count: int
    color: str | None = None


class TopicGraphEdge(BaseModel):
    source: int
    target: int
    strength: float


class TopicGraphResponse(BaseModel):
    nodes: list[TopicGraphNode]
    edges: list[TopicGraphEdge]
