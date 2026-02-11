"""Recommendation endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import recommendation_service
from app.schemas.book import BookOut

router = APIRouter()


@router.get("", response_model=list[BookOut])
async def get_recommendations(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    books = await recommendation_service.get_recommendations(db, limit=limit)
    return [BookOut.model_validate(b) for b in books]


@router.get("/similar/{book_id}")
async def get_similar_books(
    book_id: int,
    limit: int = 6,
    db: AsyncSession = Depends(get_async_session),
):
    results = await recommendation_service.get_similar_books(db, book_id, limit=limit)
    return [
        {"book": BookOut.model_validate(r["book"]), "similarity": r["similarity"]}
        for r in results
    ]
