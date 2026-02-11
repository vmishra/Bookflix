"""Content-based book recommendations."""
import logging
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.models.chunk import BookChunk
from app.models.reading import ReadingProgress
from app.models.topic import BookTopic

logger = logging.getLogger(__name__)


async def get_similar_books(db: AsyncSession, book_id: int, limit: int = 6) -> list[dict]:
    """Find similar books based on content embeddings."""
    # Get avg embedding for the source book
    result = await db.execute(
        select(BookChunk.embedding)
        .where(BookChunk.book_id == book_id)
        .where(BookChunk.embedding.isnot(None))
        .limit(20)
    )
    embeddings = [r[0] for r in result.all() if r[0] is not None]

    if not embeddings:
        return []

    avg_embedding = np.mean(embeddings, axis=0).tolist()

    # Find books with similar chunks
    result = await db.execute(
        select(
            BookChunk.book_id,
            BookChunk.embedding.cosine_distance(avg_embedding).label("distance"),
        )
        .where(BookChunk.book_id != book_id)
        .where(BookChunk.embedding.isnot(None))
        .order_by("distance")
        .limit(limit * 5)
    )
    rows = result.all()

    # Aggregate by book, take best score
    book_scores = {}
    for row in rows:
        if row.book_id not in book_scores:
            book_scores[row.book_id] = row.distance

    sorted_books = sorted(book_scores.items(), key=lambda x: x[1])[:limit]

    results = []
    for bid, distance in sorted_books:
        book = await db.get(Book, bid)
        if book:
            results.append({
                "book": book,
                "similarity": 1 - distance,
            })

    return results


async def get_recommendations(db: AsyncSession, limit: int = 10) -> list[Book]:
    """Get personalized recommendations based on reading history."""
    result = await db.execute(
        select(ReadingProgress.book_id)
        .where(ReadingProgress.status.in_(["reading", "completed"]))
        .order_by(ReadingProgress.last_read_at.desc())
        .limit(5)
    )
    read_book_ids = [r[0] for r in result.all()]

    if not read_book_ids:
        # Return popular/recent books if no history
        result = await db.execute(
            select(Book)
            .where(Book.processing_status == "completed")
            .order_by(Book.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    all_similar = []
    for bid in read_book_ids:
        similar = await get_similar_books(db, bid, limit=3)
        all_similar.extend(similar)

    seen = set(read_book_ids)
    unique = []
    for item in all_similar:
        if item["book"].id not in seen:
            seen.add(item["book"].id)
            unique.append(item["book"])

    return unique[:limit]
