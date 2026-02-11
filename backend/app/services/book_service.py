"""Book CRUD operations."""
import logging
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.book import Book, BookFile
from app.models.reading import ReadingProgress

logger = logging.getLogger(__name__)


async def get_books(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Book], int]:
    query = select(Book)
    count_query = select(func.count(Book.id))

    if status:
        query = query.where(Book.processing_status == status)
        count_query = count_query.where(Book.processing_status == status)

    order_col = getattr(Book, sort_by, Book.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)

    total = await db.scalar(count_query)
    result = await db.execute(query.offset(skip).limit(limit))
    books = result.scalars().all()

    return list(books), total or 0


async def get_book(db: AsyncSession, book_id: int) -> Book | None:
    result = await db.execute(
        select(Book)
        .where(Book.id == book_id)
        .options(
            selectinload(Book.files),
            selectinload(Book.reading_progress),
            selectinload(Book.insights),
        )
    )
    return result.scalar_one_or_none()


async def get_book_by_hash(db: AsyncSession, file_hash: str) -> Book | None:
    result = await db.execute(select(Book).where(Book.file_hash == file_hash))
    return result.scalar_one_or_none()


async def create_book(db: AsyncSession, **kwargs) -> Book:
    book = Book(**kwargs)
    db.add(book)
    await db.flush()
    return book


async def add_book_file(db: AsyncSession, book_id: int, file_path: str, file_type: str, file_size: int) -> BookFile:
    bf = BookFile(book_id=book_id, file_path=file_path, file_type=file_type, file_size=file_size)
    db.add(bf)
    await db.flush()
    return bf


async def update_book(db: AsyncSession, book_id: int, **kwargs) -> Book | None:
    book = await get_book(db, book_id)
    if not book:
        return None
    for key, value in kwargs.items():
        if hasattr(book, key):
            setattr(book, key, value)
    await db.flush()
    return book


async def delete_book(db: AsyncSession, book_id: int) -> bool:
    book = await get_book(db, book_id)
    if not book:
        return False
    await db.delete(book)
    await db.flush()
    return True


async def get_recent_books(db: AsyncSession, limit: int = 10) -> list[Book]:
    result = await db.execute(
        select(Book).order_by(desc(Book.created_at)).limit(limit)
    )
    return list(result.scalars().all())


async def get_continue_reading(db: AsyncSession, limit: int = 10) -> list[Book]:
    result = await db.execute(
        select(Book)
        .join(ReadingProgress)
        .where(ReadingProgress.status == "reading")
        .order_by(desc(ReadingProgress.last_read_at))
        .limit(limit)
    )
    return list(result.scalars().all())
