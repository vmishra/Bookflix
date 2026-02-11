"""Search schemas."""
from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: int
    book_id: int
    book_title: str | None = None
    book_author: str | None = None
    content: str
    page_number: int | None = None
    chapter: str | None = None
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    total: int


class SearchSuggestion(BaseModel):
    id: int
    title: str
    author: str | None = None
