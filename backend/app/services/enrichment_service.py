"""External metadata enrichment from Google Books / Open Library."""
import logging
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enrichment import ExternalMetadata
from app.models.book import Book

logger = logging.getLogger(__name__)

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_API = "https://openlibrary.org/search.json"


async def enrich_from_google_books(db: AsyncSession, book_id: int) -> dict | None:
    book = await db.get(Book, book_id)
    if not book:
        return None

    query = f"{book.title}"
    if book.author:
        query += f"+inauthor:{book.author}"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(GOOGLE_BOOKS_API, params={"q": query, "maxResults": 1})
            resp.raise_for_status()
            data = resp.json()

        if not data.get("items"):
            return None

        volume = data["items"][0]["volumeInfo"]

        metadata = ExternalMetadata(
            book_id=book_id,
            source="google_books",
            external_id=data["items"][0].get("id"),
            raw_data=volume,
        )
        db.add(metadata)

        # Update book with enriched data
        if not book.description and volume.get("description"):
            book.description = volume["description"]
        if not book.isbn:
            for ident in volume.get("industryIdentifiers", []):
                if ident["type"] == "ISBN_13":
                    book.isbn = ident["identifier"]
                    break
        if not book.publisher and volume.get("publisher"):
            book.publisher = volume["publisher"]
        if not book.published_date and volume.get("publishedDate"):
            book.published_date = volume["publishedDate"]
        if volume.get("averageRating"):
            book.rating = volume["averageRating"]
        if not book.page_count and volume.get("pageCount"):
            book.page_count = volume["pageCount"]

        await db.flush()
        return volume
    except Exception as e:
        logger.error(f"Google Books enrichment failed for book {book_id}: {e}")
        return None


async def fetch_cover_from_google(db: AsyncSession, book_id: int) -> bytes | None:
    result = await db.execute(
        select(ExternalMetadata)
        .where(ExternalMetadata.book_id == book_id)
        .where(ExternalMetadata.source == "google_books")
    )
    metadata = result.scalar_one_or_none()

    if not metadata or not metadata.raw_data:
        return None

    image_links = metadata.raw_data.get("imageLinks", {})
    url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

    if not url:
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
    except Exception as e:
        logger.error(f"Cover fetch failed for book {book_id}: {e}")
        return None
