"""AI insight generation and retrieval."""
import json
import logging
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.insight import BookInsight, InsightConnection
from app.models.book import Book
from app.models.chunk import BookChunk
from app.llm.client import llm_client
from app.llm.prompts import (
    SYSTEM_INSIGHT, EXTRACT_KEY_CONCEPTS, EXTRACT_FRAMEWORKS,
    EXTRACT_TAKEAWAYS, GENERATE_SUMMARY,
)
from app.processing.embedder import generate_single_embedding

logger = logging.getLogger(__name__)


async def get_book_insights(
    db: AsyncSession,
    book_id: int,
    insight_type: str | None = None,
) -> list[BookInsight]:
    query = select(BookInsight).where(BookInsight.book_id == book_id)
    if insight_type:
        query = query.where(BookInsight.insight_type == insight_type)
    query = query.order_by(desc(BookInsight.importance))
    result = await db.execute(query)
    return list(result.scalars().all())


async def generate_insights_for_book(
    db: AsyncSession,
    book_id: int,
    pass_level: int = 1,
) -> list[BookInsight]:
    book = await db.get(Book, book_id)
    if not book:
        return []

    # Get representative chunks
    chunk_limit = 20 if pass_level == 1 else 50
    result = await db.execute(
        select(BookChunk)
        .where(BookChunk.book_id == book_id)
        .order_by(BookChunk.chunk_index)
        .limit(chunk_limit)
    )
    chunks = list(result.scalars().all())
    if not chunks:
        return []

    content = "\n\n---\n\n".join(c.content for c in chunks)
    insights = []

    # Extract concepts
    try:
        response = await llm_client.complete(
            messages=[
                {"role": "system", "content": SYSTEM_INSIGHT},
                {"role": "user", "content": EXTRACT_KEY_CONCEPTS.format(
                    title=book.title, author=book.author or "Unknown", content=content[:50000]
                )},
            ],
            task_type="insight",
        )
        data = json.loads(response)
        for concept in data.get("concepts", []):
            embedding = generate_single_embedding(f"{concept['title']}: {concept['content']}")
            insight = BookInsight(
                book_id=book_id,
                insight_type="key_concept",
                title=concept["title"],
                content=concept["content"],
                supporting_quote=concept.get("supporting_quote"),
                importance=concept.get("importance", 5),
                refinement_level=pass_level,
                embedding=embedding,
            )
            db.add(insight)
            insights.append(insight)
    except Exception as e:
        logger.error(f"Concept extraction failed for book {book_id}: {e}")

    # Extract frameworks
    try:
        response = await llm_client.complete(
            messages=[
                {"role": "system", "content": SYSTEM_INSIGHT},
                {"role": "user", "content": EXTRACT_FRAMEWORKS.format(
                    title=book.title, author=book.author or "Unknown", content=content[:50000]
                )},
            ],
            task_type="insight",
        )
        data = json.loads(response)
        for fw in data.get("frameworks", []):
            embedding = generate_single_embedding(f"{fw['title']}: {fw['content']}")
            insight = BookInsight(
                book_id=book_id,
                insight_type="framework",
                title=fw["title"],
                content=fw["content"],
                supporting_quote=fw.get("supporting_quote"),
                importance=fw.get("importance", 5),
                refinement_level=pass_level,
                embedding=embedding,
            )
            db.add(insight)
            insights.append(insight)
    except Exception as e:
        logger.error(f"Framework extraction failed for book {book_id}: {e}")

    # Extract takeaways
    try:
        response = await llm_client.complete(
            messages=[
                {"role": "system", "content": SYSTEM_INSIGHT},
                {"role": "user", "content": EXTRACT_TAKEAWAYS.format(
                    title=book.title, author=book.author or "Unknown", content=content[:50000]
                )},
            ],
            task_type="insight",
        )
        data = json.loads(response)
        for tw in data.get("takeaways", []):
            embedding = generate_single_embedding(f"{tw['title']}: {tw['content']}")
            insight = BookInsight(
                book_id=book_id,
                insight_type="takeaway",
                title=tw["title"],
                content=tw["content"],
                importance=tw.get("importance", 5),
                refinement_level=pass_level,
                embedding=embedding,
            )
            db.add(insight)
            insights.append(insight)
    except Exception as e:
        logger.error(f"Takeaway extraction failed for book {book_id}: {e}")

    await db.flush()
    return insights


async def find_insight_connections(
    db: AsyncSession,
    insight_id: int,
    limit: int = 5,
) -> list[dict]:
    insight = await db.get(BookInsight, insight_id)
    if not insight or insight.embedding is None:
        return []

    result = await db.execute(
        select(BookInsight)
        .where(BookInsight.id != insight_id)
        .where(BookInsight.book_id != insight.book_id)
        .where(BookInsight.embedding.isnot(None))
        .order_by(BookInsight.embedding.cosine_distance(insight.embedding))
        .limit(limit)
    )
    similar = result.scalars().all()

    connections = []
    for s in similar:
        connections.append({
            "insight_id": s.id,
            "book_id": s.book_id,
            "title": s.title,
            "content": s.content,
            "type": s.insight_type,
        })
    return connections
