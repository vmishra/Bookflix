"""Topic modeling and knowledge graph."""
import logging
import numpy as np
from sklearn.cluster import KMeans
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.topic import Topic, BookTopic, TopicRelation
from app.models.book import Book
from app.models.chunk import BookChunk
from app.processing.embedder import generate_single_embedding

logger = logging.getLogger(__name__)


async def get_topics(db: AsyncSession) -> list[Topic]:
    result = await db.execute(
        select(Topic).order_by(Topic.book_count.desc())
    )
    return list(result.scalars().all())


async def get_topic_with_books(db: AsyncSession, topic_id: int) -> dict | None:
    topic = await db.get(Topic, topic_id)
    if not topic:
        return None

    result = await db.execute(
        select(Book)
        .join(BookTopic)
        .where(BookTopic.topic_id == topic_id)
        .order_by(BookTopic.relevance.desc())
    )
    books = list(result.scalars().all())

    return {"topic": topic, "books": books}


async def get_topic_graph(db: AsyncSession) -> dict:
    topics = await get_topics(db)
    result = await db.execute(select(TopicRelation).where(TopicRelation.strength > 0.3))
    relations = result.scalars().all()

    nodes = [
        {"id": t.id, "name": t.name, "book_count": t.book_count, "color": t.color}
        for t in topics
    ]
    edges = [
        {"source": r.topic_a_id, "target": r.topic_b_id, "strength": r.strength}
        for r in relations
    ]

    return {"nodes": nodes, "edges": edges}


async def run_topic_modeling(db: AsyncSession, n_topics: int = 10) -> list[Topic]:
    """K-means clustering on book embeddings -> topics."""
    result = await db.execute(
        select(Book.id)
        .where(Book.processing_status == "completed")
    )
    book_ids = [r[0] for r in result.all()]

    if len(book_ids) < n_topics:
        n_topics = max(2, len(book_ids) // 2)

    # Get average embedding per book
    book_embeddings = []
    valid_book_ids = []
    for bid in book_ids:
        chunk_result = await db.execute(
            select(BookChunk.embedding)
            .where(BookChunk.book_id == bid)
            .where(BookChunk.embedding.isnot(None))
            .limit(20)
        )
        embeddings = [r[0] for r in chunk_result.all() if r[0] is not None]
        if embeddings:
            avg = np.mean(embeddings, axis=0)
            book_embeddings.append(avg)
            valid_book_ids.append(bid)

    if len(book_embeddings) < 2:
        return []

    X = np.array(book_embeddings)
    kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    topics = []
    for i in range(n_topics):
        cluster_books = [valid_book_ids[j] for j in range(len(labels)) if labels[j] == i]
        if not cluster_books:
            continue

        center = kmeans.cluster_centers_[i].tolist()
        topic = Topic(
            name=f"Topic {i + 1}",
            embedding=center,
            book_count=len(cluster_books),
            color=f"#{hash(f'topic{i}') % 0xFFFFFF:06x}",
        )
        db.add(topic)
        await db.flush()

        for bid in cluster_books:
            bt = BookTopic(book_id=bid, topic_id=topic.id, relevance=0.8)
            db.add(bt)

        topics.append(topic)

    await db.flush()
    return topics
