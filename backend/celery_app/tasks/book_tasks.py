"""Book scanning, extraction, and chunking tasks."""
import logging
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.models.book import Book, BookFile
from app.models.chunk import BookChunk
from app.models.processing import ProcessingJob
from app.processing.extractors.pdf_extractor import PDFExtractor
from app.processing.extractors.epub_extractor import EPUBExtractor
from app.processing.chunker import TextChunker
from app.processing.pipeline import compute_file_hash, save_cover_image, scan_directory
from app.processing.metadata_parser import parse_filename
from sqlalchemy import select
import datetime

logger = logging.getLogger(__name__)


@celery_app.task(name="celery_app.tasks.book_tasks.scan_library")
def scan_library(directory: str) -> dict:
    """Scan directory for books and import them."""
    files = scan_directory(directory)

    with sync_session_factory() as db:
        imported = 0
        skipped = 0

        for file_info in files:
            try:
                file_hash = compute_file_hash(file_info["file_path"])

                existing = db.execute(
                    select(Book).where(Book.file_hash == file_hash)
                ).scalar_one_or_none()

                if existing:
                    skipped += 1
                    continue

                parsed = parse_filename(file_info["file_path"])
                book = Book(
                    title=parsed["title"],
                    author=parsed.get("author"),
                    file_hash=file_hash,
                    processing_status="pending",
                )
                db.add(book)
                db.flush()

                book_file = BookFile(
                    book_id=book.id,
                    file_path=file_info["file_path"],
                    file_type=file_info["file_type"],
                    file_size=file_info["file_size"],
                )
                db.add(book_file)

                # Create processing jobs for the pipeline
                for stage in ["extract", "chunk", "embed", "insights_pass_1", "enrichment"]:
                    job = ProcessingJob(
                        book_id=book.id,
                        stage=stage,
                        status="pending",
                    )
                    db.add(job)

                imported += 1
            except Exception as e:
                logger.error(f"Error importing {file_info['file_path']}: {e}")

        db.commit()

    return {"imported": imported, "skipped": skipped, "total_found": len(files)}


@celery_app.task(name="celery_app.tasks.book_tasks.extract_text", bind=True)
def extract_text(self, book_id: int) -> dict:
    """Extract text from a book file."""
    with sync_session_factory() as db:
        book = db.get(Book, book_id)
        if not book:
            return {"error": "Book not found"}

        # Update status
        book.processing_status = "extracting"

        # Update processing job
        job = db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.book_id == book_id)
            .where(ProcessingJob.stage == "extract")
        ).scalar_one_or_none()

        if job:
            job.status = "running"
            job.celery_task_id = self.request.id
            job.started_at = datetime.datetime.utcnow()
            job.attempts += 1

        db.commit()

        # Get book file
        book_file = db.execute(
            select(BookFile).where(BookFile.book_id == book_id)
        ).scalar_one_or_none()

        if not book_file:
            if job:
                job.status = "failed"
                job.error_message = "No file found"
                db.commit()
            return {"error": "No file found"}

        try:
            if book_file.file_type == "pdf":
                extractor = PDFExtractor()
                result = extractor.extract(book_file.file_path)

                # Update book metadata from extraction
                if result.title and (not book.title or book.title == parse_filename(book_file.file_path)["title"]):
                    book.title = result.title
                if result.author and not book.author:
                    book.author = result.author
                book.page_count = result.total_pages

                # Save cover
                if result.cover_image:
                    from app.utils.image_utils import resize_cover
                    resized = resize_cover(result.cover_image)
                    cover_path = save_cover_image(book.id, resized)
                    book.cover_path = cover_path

                # Update search vector
                all_text = " ".join(p.text[:500] for p in result.pages[:10])
                from sqlalchemy import text as sql_text
                db.execute(
                    sql_text(
                        "UPDATE books SET search_vector = to_tsvector('english', :text) WHERE id = :id"
                    ),
                    {"text": f"{book.title} {book.author or ''} {all_text[:5000]}", "id": book.id}
                )

                page_count = len(result.pages)

            elif book_file.file_type == "epub":
                extractor = EPUBExtractor()
                result = extractor.extract(book_file.file_path)

                if result.title and (not book.title or book.title == parse_filename(book_file.file_path)["title"]):
                    book.title = result.title
                if result.author and not book.author:
                    book.author = result.author

                if result.cover_image:
                    from app.utils.image_utils import resize_cover
                    resized = resize_cover(result.cover_image)
                    cover_path = save_cover_image(book.id, resized)
                    book.cover_path = cover_path

                all_text = " ".join(ch.text[:500] for ch in result.chapters[:10])
                from sqlalchemy import text as sql_text
                db.execute(
                    sql_text(
                        "UPDATE books SET search_vector = to_tsvector('english', :text) WHERE id = :id"
                    ),
                    {"text": f"{book.title} {book.author or ''} {all_text[:5000]}", "id": book.id}
                )

                page_count = result.total_chapters
            else:
                raise ValueError(f"Unsupported file type: {book_file.file_type}")

            if job:
                job.status = "completed"
                job.completed_at = datetime.datetime.utcnow()

            db.commit()

            # Chain to chunking
            chunk_text.delay(book_id)

            return {"book_id": book_id, "pages": page_count}

        except Exception as e:
            logger.error(f"Extraction failed for book {book_id}: {e}")
            book.processing_status = "failed"
            if job:
                job.status = "failed"
                job.error_message = str(e)
            db.commit()
            return {"error": str(e)}


@celery_app.task(name="celery_app.tasks.book_tasks.chunk_text", bind=True)
def chunk_text(self, book_id: int) -> dict:
    """Chunk extracted text into smaller pieces."""
    with sync_session_factory() as db:
        book = db.get(Book, book_id)
        if not book:
            return {"error": "Book not found"}

        book.processing_status = "chunking"

        job = db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.book_id == book_id)
            .where(ProcessingJob.stage == "chunk")
        ).scalar_one_or_none()

        if job:
            job.status = "running"
            job.celery_task_id = self.request.id
            job.started_at = datetime.datetime.utcnow()
            job.attempts += 1

        db.commit()

        book_file = db.execute(
            select(BookFile).where(BookFile.book_id == book_id)
        ).scalar_one_or_none()

        if not book_file:
            return {"error": "No file found"}

        try:
            chunker = TextChunker(chunk_size=512, chunk_overlap=64)

            if book_file.file_type == "pdf":
                extractor = PDFExtractor()
                result = extractor.extract(book_file.file_path)
                pages = [{"text": p.text, "page_number": p.page_number, "chapter": p.chapter} for p in result.pages]
                chunks = chunker.chunk_pages(pages)
            elif book_file.file_type == "epub":
                extractor = EPUBExtractor()
                result = extractor.extract(book_file.file_path)
                pages = [{"text": ch.text, "page_number": ch.index + 1, "chapter": ch.title} for ch in result.chapters]
                chunks = chunker.chunk_pages(pages)
            else:
                raise ValueError(f"Unsupported: {book_file.file_type}")

            # Delete existing chunks
            db.execute(
                select(BookChunk).where(BookChunk.book_id == book_id)
            )
            from sqlalchemy import delete
            db.execute(delete(BookChunk).where(BookChunk.book_id == book_id))

            # Store new chunks
            for chunk in chunks:
                from sqlalchemy import text as sql_text
                db_chunk = BookChunk(
                    book_id=book_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.text,
                    page_number=chunk.page_number,
                    chapter=chunk.chapter,
                    token_count=chunk.token_count,
                )
                db.add(db_chunk)

            db.flush()

            # Update search vectors for chunks
            from sqlalchemy import text as sql_text
            db.execute(
                sql_text(
                    "UPDATE book_chunks SET search_vector = to_tsvector('english', content) WHERE book_id = :id"
                ),
                {"id": book_id}
            )

            if job:
                job.status = "completed"
                job.completed_at = datetime.datetime.utcnow()

            db.commit()

            # Chain to embedding
            from celery_app.tasks.embedding_tasks import generate_book_embeddings
            generate_book_embeddings.delay(book_id)

            return {"book_id": book_id, "chunks": len(chunks)}

        except Exception as e:
            logger.error(f"Chunking failed for book {book_id}: {e}")
            if job:
                job.status = "failed"
                job.error_message = str(e)
            db.commit()
            return {"error": str(e)}


@celery_app.task(name="celery_app.tasks.book_tasks.process_book")
def process_book(book_id: int) -> dict:
    """Start the full processing pipeline for a book."""
    extract_text.delay(book_id)
    return {"book_id": book_id, "status": "pipeline_started"}
