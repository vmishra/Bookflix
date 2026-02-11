"""Book endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import book_service
from app.schemas.book import BookOut, BookDetailOut, BookUpdate, BookListResponse
from app.config import settings
import os

router = APIRouter()


@router.get("", response_model=BookListResponse)
async def list_books(
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_async_session),
):
    books, total = await book_service.get_books(db, skip=skip, limit=limit, status=status, sort_by=sort_by, sort_order=sort_order)
    return BookListResponse(
        items=[BookOut.model_validate(b) for b in books],
        total=total, skip=skip, limit=limit,
    )


@router.get("/recent", response_model=list[BookOut])
async def recent_books(limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    books = await book_service.get_recent_books(db, limit=limit)
    return [BookOut.model_validate(b) for b in books]


@router.get("/continue-reading", response_model=list[BookOut])
async def continue_reading(limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    books = await book_service.get_continue_reading(db, limit=limit)
    return [BookOut.model_validate(b) for b in books]


@router.get("/{book_id}", response_model=BookDetailOut)
async def get_book(book_id: int, db: AsyncSession = Depends(get_async_session)):
    book = await book_service.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookDetailOut.model_validate(book)


@router.get("/{book_id}/file")
async def get_book_file(book_id: int, db: AsyncSession = Depends(get_async_session)):
    book = await book_service.get_book(db, book_id)
    if not book or not book.files:
        raise HTTPException(status_code=404, detail="Book file not found")

    file = book.files[0]
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_type = "application/pdf" if file.file_type == "pdf" else "application/epub+zip"
    return FileResponse(
        file.file_path,
        media_type=media_type,
        filename=f"{book.title}.{file.file_type}",
    )


@router.get("/{book_id}/cover")
async def get_book_cover(book_id: int, db: AsyncSession = Depends(get_async_session)):
    book = await book_service.get_book(db, book_id)
    if not book or not book.cover_path:
        raise HTTPException(status_code=404, detail="Cover not found")

    cover_full_path = os.path.join(settings.covers_path, book.cover_path)
    if not os.path.exists(cover_full_path):
        raise HTTPException(status_code=404, detail="Cover file not found")

    return FileResponse(cover_full_path, media_type="image/png")


@router.patch("/{book_id}", response_model=BookOut)
async def update_book(book_id: int, update: BookUpdate, db: AsyncSession = Depends(get_async_session)):
    book = await book_service.update_book(db, book_id, **update.model_dump(exclude_unset=True))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookOut.model_validate(book)


@router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_async_session)):
    success = await book_service.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
