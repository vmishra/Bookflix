"""Embedding generation tasks."""
import logging
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.models.book import Book
from app.models.chunk import BookChunk
from app.models.processing import ProcessingJob
from app.processing.embedder import generate_embeddings
from sqlalchemy import select
import datetime

logger = logging.getLogger(__name__)


@celery_app.task(name="celery_app.tasks.embedding_tasks.generate_book_embeddings", bind=True)
def generate_book_embeddings(self, book_id: int, batch_size: int = 64) -> dict:
    """Generate embeddings for all chunks of a book."""
    with sync_session_factory() as db:
        book = db.get(Book, book_id)
        if not book:
            return {"error": "Book not found"}

        book.processing_status = "embedding"

        job = db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.book_id == book_id)
            .where(ProcessingJob.stage == "embed")
        ).scalar_one_or_none()

        if job:
            job.status = "running"
            job.celery_task_id = self.request.id
            job.started_at = datetime.datetime.utcnow()
            job.attempts += 1

        db.commit()

        try:
            chunks = db.execute(
                select(BookChunk)
                .where(BookChunk.book_id == book_id)
                .where(BookChunk.embedding.is_(None))
                .order_by(BookChunk.chunk_index)
            ).scalars().all()

            if not chunks:
                if job:
                    job.status = "completed"
                    job.completed_at = datetime.datetime.utcnow()
                db.commit()
                return {"book_id": book_id, "embedded": 0}

            total = 0
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                texts = [c.content for c in batch]
                embeddings = generate_embeddings(texts, batch_size=batch_size)

                for chunk, emb in zip(batch, embeddings):
                    chunk.embedding = emb

                total += len(batch)

                # Update progress
                progress = total / len(chunks) * 100
                book.processing_progress = progress
                db.commit()

            if job:
                job.status = "completed"
                job.completed_at = datetime.datetime.utcnow()

            db.commit()

            # Chain to insights
            from celery_app.tasks.insight_tasks import generate_book_insights
            generate_book_insights.delay(book_id, pass_level=1)

            return {"book_id": book_id, "embedded": total}

        except Exception as e:
            logger.error(f"Embedding failed for book {book_id}: {e}")
            if job:
                job.status = "failed"
                job.error_message = str(e)
            db.commit()
            return {"error": str(e)}
