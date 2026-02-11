"""Second brain - learning paths and knowledge connections."""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import LearningPath, LearningPathBook
from app.models.insight import InsightConnection, BookInsight
from app.models.book import Book

logger = logging.getLogger(__name__)


async def get_learning_paths(db: AsyncSession) -> list[LearningPath]:
    result = await db.execute(
        select(LearningPath).order_by(LearningPath.created_at.desc())
    )
    return list(result.scalars().all())


async def get_learning_path(db: AsyncSession, path_id: int) -> dict | None:
    path = await db.get(LearningPath, path_id)
    if not path:
        return None

    result = await db.execute(
        select(LearningPathBook)
        .where(LearningPathBook.path_id == path_id)
        .order_by(LearningPathBook.position)
    )
    path_books = result.scalars().all()

    books = []
    for pb in path_books:
        book = await db.get(Book, pb.book_id)
        if book:
            books.append({"book": book, "position": pb.position, "rationale": pb.rationale})

    return {"path": path, "books": books}


async def get_knowledge_connections(db: AsyncSession, limit: int = 50) -> list[dict]:
    result = await db.execute(
        select(InsightConnection)
        .order_by(InsightConnection.strength.desc())
        .limit(limit)
    )
    connections = result.scalars().all()

    results = []
    for conn in connections:
        insight_a = await db.get(BookInsight, conn.insight_a_id)
        insight_b = await db.get(BookInsight, conn.insight_b_id)
        if insight_a and insight_b:
            book_a = await db.get(Book, insight_a.book_id)
            book_b = await db.get(Book, insight_b.book_id)
            results.append({
                "connection": conn,
                "insight_a": {"insight": insight_a, "book": book_a},
                "insight_b": {"insight": insight_b, "book": book_b},
            })

    return results


async def get_knowledge_map(db: AsyncSession) -> dict:
    """Build a knowledge map of all book connections."""
    result = await db.execute(
        select(Book).where(Book.processing_status == "completed")
    )
    books = result.scalars().all()

    result = await db.execute(
        select(InsightConnection).where(InsightConnection.strength > 0.5)
    )
    connections = result.scalars().all()

    book_ids_in_connections = set()
    edges = []
    for conn in connections:
        insight_a = await db.get(BookInsight, conn.insight_a_id)
        insight_b = await db.get(BookInsight, conn.insight_b_id)
        if insight_a and insight_b and insight_a.book_id != insight_b.book_id:
            book_ids_in_connections.add(insight_a.book_id)
            book_ids_in_connections.add(insight_b.book_id)
            edges.append({
                "source": insight_a.book_id,
                "target": insight_b.book_id,
                "strength": conn.strength,
                "description": conn.description,
            })

    nodes = [
        {"id": b.id, "title": b.title, "author": b.author}
        for b in books if b.id in book_ids_in_connections
    ]

    return {"nodes": nodes, "edges": edges}
