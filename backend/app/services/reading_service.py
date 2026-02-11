"""Reading progress and session tracking."""
import logging
import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reading import ReadingProgress, ReadingSession

logger = logging.getLogger(__name__)


async def get_reading_progress(db: AsyncSession, book_id: int) -> ReadingProgress | None:
    result = await db.execute(
        select(ReadingProgress).where(ReadingProgress.book_id == book_id)
    )
    return result.scalar_one_or_none()


async def update_reading_progress(
    db: AsyncSession,
    book_id: int,
    current_page: int | None = None,
    total_pages: int | None = None,
    epub_cfi: str | None = None,
) -> ReadingProgress:
    progress = await get_reading_progress(db, book_id)

    if not progress:
        progress = ReadingProgress(book_id=book_id)
        db.add(progress)

    if current_page is not None:
        progress.current_page = current_page
    if total_pages is not None:
        progress.total_pages = total_pages
    if epub_cfi is not None:
        progress.epub_cfi = epub_cfi

    if progress.total_pages and progress.total_pages > 0:
        progress.progress_percent = (progress.current_page / progress.total_pages) * 100
        if progress.progress_percent >= 95:
            progress.status = "completed"
        elif progress.current_page > 0:
            progress.status = "reading"

    progress.last_read_at = datetime.datetime.utcnow()
    await db.flush()
    return progress


async def start_reading_session(db: AsyncSession, book_id: int) -> ReadingSession:
    session = ReadingSession(book_id=book_id)
    db.add(session)
    await db.flush()
    return session


async def end_reading_session(
    db: AsyncSession,
    session_id: int,
    pages_read: int = 0,
) -> ReadingSession | None:
    session = await db.get(ReadingSession, session_id)
    if not session:
        return None

    session.ended_at = datetime.datetime.utcnow()
    session.pages_read = pages_read
    if session.started_at:
        delta = session.ended_at - session.started_at
        session.duration = int(delta.total_seconds())

    # Update total read time in progress
    progress = await get_reading_progress(db, session.book_id)
    if progress and session.duration:
        progress.total_read_time = (progress.total_read_time or 0) + session.duration

    await db.flush()
    return session


async def get_reading_stats(db: AsyncSession) -> dict:
    total_time = await db.scalar(
        select(func.sum(ReadingProgress.total_read_time))
    ) or 0

    books_completed = await db.scalar(
        select(func.count(ReadingProgress.id))
        .where(ReadingProgress.status == "completed")
    ) or 0

    books_reading = await db.scalar(
        select(func.count(ReadingProgress.id))
        .where(ReadingProgress.status == "reading")
    ) or 0

    return {
        "total_read_time_seconds": total_time,
        "total_read_time_hours": round(total_time / 3600, 1),
        "books_completed": books_completed,
        "books_reading": books_reading,
    }
