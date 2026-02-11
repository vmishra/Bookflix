"""Search endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import search_service
from app.schemas.search import SearchResponse, SearchResult, SearchSuggestion
from app.schemas.book import BookOut

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    book_ids: str | None = None,
    db: AsyncSession = Depends(get_async_session),
):
    bid_list = [int(x) for x in book_ids.split(",")] if book_ids else None
    results = await search_service.hybrid_search(db, q, limit=limit, book_ids=bid_list)
    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        query=q,
        total=len(results),
    )


@router.get("/suggest", response_model=list[SearchSuggestion])
async def search_suggest(
    q: str = Query(..., min_length=1),
    limit: int = 5,
    db: AsyncSession = Depends(get_async_session),
):
    suggestions = await search_service.suggest_search(db, q, limit=limit)
    return [SearchSuggestion(**s) for s in suggestions]


@router.get("/books", response_model=list[BookOut])
async def search_books(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session),
):
    books = await search_service.search_books(db, q, limit=limit)
    return [BookOut.model_validate(b) for b in books]
