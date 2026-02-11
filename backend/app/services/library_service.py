"""Library scanning and import service."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.processing.pipeline import scan_directory, compute_file_hash
from app.processing.metadata_parser import parse_filename
from app.services.book_service import get_book_by_hash, create_book, add_book_file

logger = logging.getLogger(__name__)


async def scan_books_directory(directory: str) -> list[dict]:
    return scan_directory(directory)


async def import_books(db: AsyncSession, files: list[dict]) -> dict:
    imported = 0
    skipped = 0
    errors = 0

    for file_info in files:
        try:
            file_hash = compute_file_hash(file_info["file_path"])
            existing = await get_book_by_hash(db, file_hash)

            if existing:
                skipped += 1
                continue

            parsed = parse_filename(file_info["file_path"])
            book = await create_book(
                db,
                title=parsed["title"],
                author=parsed.get("author"),
                file_hash=file_hash,
                processing_status="pending",
            )

            await add_book_file(
                db,
                book_id=book.id,
                file_path=file_info["file_path"],
                file_type=file_info["file_type"],
                file_size=file_info["file_size"],
            )

            imported += 1
        except Exception as e:
            logger.error(f"Error importing {file_info['file_path']}: {e}")
            errors += 1

    return {"imported": imported, "skipped": skipped, "errors": errors}


async def get_library_stats(db: AsyncSession) -> dict:
    from sqlalchemy import select, func
    from app.models.book import Book
    from app.models.chunk import BookChunk
    from app.models.insight import BookInsight

    total_books = await db.scalar(select(func.count(Book.id))) or 0
    processed = await db.scalar(
        select(func.count(Book.id)).where(Book.processing_status == "completed")
    ) or 0
    total_chunks = await db.scalar(select(func.count(BookChunk.id))) or 0
    total_insights = await db.scalar(select(func.count(BookInsight.id))) or 0

    return {
        "total_books": total_books,
        "processed_books": processed,
        "pending_books": total_books - processed,
        "total_chunks": total_chunks,
        "total_insights": total_insights,
    }
