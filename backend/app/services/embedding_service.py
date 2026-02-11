"""Embedding generation service for book chunks."""
import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chunk import BookChunk
from app.processing.embedder import generate_embeddings

logger = logging.getLogger(__name__)


async def embed_book_chunks(db: AsyncSession, book_id: int, batch_size: int = 64) -> int:
    """Generate embeddings for all chunks of a book. Returns count embedded."""
    result = await db.execute(
        select(BookChunk)
        .where(BookChunk.book_id == book_id)
        .where(BookChunk.embedding.is_(None))
        .order_by(BookChunk.chunk_index)
    )
    chunks = list(result.scalars().all())

    if not chunks:
        return 0

    total = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.content for c in batch]
        embeddings = generate_embeddings(texts, batch_size=batch_size)

        for chunk, emb in zip(batch, embeddings):
            chunk.embedding = emb

        total += len(batch)

    await db.flush()
    logger.info(f"Embedded {total} chunks for book {book_id}")
    return total
