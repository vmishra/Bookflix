"""Reading progress endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import reading_service
from app.schemas.reading import ReadingProgressOut, ReadingProgressUpdate, ReadingStatsOut

router = APIRouter()


@router.get("/progress/{book_id}", response_model=ReadingProgressOut | None)
async def get_progress(book_id: int, db: AsyncSession = Depends(get_async_session)):
    progress = await reading_service.get_reading_progress(db, book_id)
    if not progress:
        return None
    return ReadingProgressOut.model_validate(progress)


@router.put("/progress/{book_id}", response_model=ReadingProgressOut)
async def update_progress(
    book_id: int,
    update: ReadingProgressUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    progress = await reading_service.update_reading_progress(
        db, book_id,
        current_page=update.current_page,
        total_pages=update.total_pages,
        epub_cfi=update.epub_cfi,
    )
    return ReadingProgressOut.model_validate(progress)


@router.post("/sessions/{book_id}/start")
async def start_session(book_id: int, db: AsyncSession = Depends(get_async_session)):
    session = await reading_service.start_reading_session(db, book_id)
    return {"session_id": session.id}


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: int,
    pages_read: int = 0,
    db: AsyncSession = Depends(get_async_session),
):
    session = await reading_service.end_reading_session(db, session_id, pages_read=pages_read)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"duration": session.duration, "pages_read": session.pages_read}


@router.get("/stats", response_model=ReadingStatsOut)
async def reading_stats(db: AsyncSession = Depends(get_async_session)):
    stats = await reading_service.get_reading_stats(db)
    return ReadingStatsOut(**stats)
