"""Hybrid search: full-text + semantic + reciprocal rank fusion."""
import logging
from sqlalchemy import select, text, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.models.book import Book
from app.models.chunk import BookChunk
from app.processing.embedder import generate_single_embedding

logger = logging.getLogger(__name__)


async def hybrid_search(
    db: AsyncSession,
    query: str,
    limit: int = 20,
    book_ids: list[int] | None = None,
) -> list[dict]:
    query_embedding = generate_single_embedding(query)

    # Full-text search results
    fts_query = (
        select(
            BookChunk.id,
            BookChunk.book_id,
            BookChunk.content,
            BookChunk.page_number,
            BookChunk.chapter,
            func.ts_rank(BookChunk.search_vector, func.plainto_tsquery("english", query)).label("fts_rank"),
        )
        .where(BookChunk.search_vector.op("@@")(func.plainto_tsquery("english", query)))
        .order_by(desc("fts_rank"))
        .limit(limit * 2)
    )

    if book_ids:
        fts_query = fts_query.where(BookChunk.book_id.in_(book_ids))

    fts_result = await db.execute(fts_query)
    fts_rows = fts_result.all()

    # Semantic search results
    sem_query = (
        select(
            BookChunk.id,
            BookChunk.book_id,
            BookChunk.content,
            BookChunk.page_number,
            BookChunk.chapter,
            BookChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .where(BookChunk.embedding.isnot(None))
        .order_by("distance")
        .limit(limit * 2)
    )

    if book_ids:
        sem_query = sem_query.where(BookChunk.book_id.in_(book_ids))

    sem_result = await db.execute(sem_query)
    sem_rows = sem_result.all()

    # Reciprocal Rank Fusion
    k = 60
    scores = {}
    chunk_data = {}

    for rank, row in enumerate(fts_rows):
        scores[row.id] = scores.get(row.id, 0) + 1.0 / (k + rank + 1)
        chunk_data[row.id] = {
            "chunk_id": row.id,
            "book_id": row.book_id,
            "content": row.content,
            "page_number": row.page_number,
            "chapter": row.chapter,
        }

    for rank, row in enumerate(sem_rows):
        scores[row.id] = scores.get(row.id, 0) + 1.0 / (k + rank + 1)
        if row.id not in chunk_data:
            chunk_data[row.id] = {
                "chunk_id": row.id,
                "book_id": row.book_id,
                "content": row.content,
                "page_number": row.page_number,
                "chapter": row.chapter,
            }

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]

    results = []
    for chunk_id, score in ranked:
        data = chunk_data[chunk_id]
        data["score"] = score

        book = await db.get(Book, data["book_id"])
        if book:
            data["book_title"] = book.title
            data["book_author"] = book.author

        results.append(data)

    return results


async def search_books(
    db: AsyncSession,
    query: str,
    limit: int = 20,
) -> list[Book]:
    result = await db.execute(
        select(Book)
        .where(Book.search_vector.op("@@")(func.plainto_tsquery("english", query)))
        .order_by(
            desc(func.ts_rank(Book.search_vector, func.plainto_tsquery("english", query)))
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def suggest_search(db: AsyncSession, query: str, limit: int = 5) -> list[dict]:
    result = await db.execute(
        select(Book.id, Book.title, Book.author)
        .where(
            func.lower(Book.title).contains(query.lower())
            | func.lower(Book.author).contains(query.lower())
        )
        .limit(limit)
    )
    return [{"id": r.id, "title": r.title, "author": r.author} for r in result.all()]
