"""External metadata enrichment tasks."""
import logging
import httpx
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.models.book import Book
from app.models.enrichment import ExternalMetadata
from app.models.processing import ProcessingJob
from app.processing.pipeline import save_cover_image
from app.utils.image_utils import resize_cover
from sqlalchemy import select
import datetime

logger = logging.getLogger(__name__)

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"


@celery_app.task(name="celery_app.tasks.enrichment_tasks.enrich_book")
def enrich_book(book_id: int) -> dict:
    """Enrich book metadata from external APIs."""
    with sync_session_factory() as db:
        book = db.get(Book, book_id)
        if not book:
            return {"error": "Book not found"}

        job = db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.book_id == book_id)
            .where(ProcessingJob.stage == "enrichment")
        ).scalar_one_or_none()

        if job:
            job.status = "running"
            job.started_at = datetime.datetime.utcnow()
            job.attempts += 1

        db.commit()

        try:
            query = f"{book.title}"
            if book.author:
                query += f"+inauthor:{book.author}"

            with httpx.Client(timeout=15) as client:
                resp = client.get(GOOGLE_BOOKS_API, params={"q": query, "maxResults": 1})
                resp.raise_for_status()
                data = resp.json()

            if not data.get("items"):
                if job:
                    job.status = "completed"
                    job.completed_at = datetime.datetime.utcnow()
                db.commit()
                return {"book_id": book_id, "enriched": False}

            volume = data["items"][0]["volumeInfo"]

            metadata = ExternalMetadata(
                book_id=book_id,
                source="google_books",
                external_id=data["items"][0].get("id"),
                raw_data=volume,
            )
            db.add(metadata)

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

            # Fetch cover if not already present
            if not book.cover_path:
                image_links = volume.get("imageLinks", {})
                url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
                if url:
                    try:
                        with httpx.Client(timeout=15) as client:
                            resp = client.get(url)
                            resp.raise_for_status()
                            resized = resize_cover(resp.content)
                            cover_path = save_cover_image(book.id, resized)
                            book.cover_path = cover_path
                    except Exception as e:
                        logger.warning(f"Cover fetch failed: {e}")

            if job:
                job.status = "completed"
                job.completed_at = datetime.datetime.utcnow()

            db.commit()
            return {"book_id": book_id, "enriched": True}

        except Exception as e:
            logger.error(f"Enrichment failed for book {book_id}: {e}")
            if job:
                job.status = "failed"
                job.error_message = str(e)
            db.commit()
            return {"error": str(e)}
