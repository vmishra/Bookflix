"""Topic modeling tasks."""
import logging
import numpy as np
from sklearn.cluster import KMeans
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.models.book import Book
from app.models.chunk import BookChunk
from app.models.topic import Topic, BookTopic, TopicRelation
from sqlalchemy import select, delete, func

logger = logging.getLogger(__name__)


@celery_app.task(name="celery_app.tasks.topic_tasks.rebuild_topics")
def rebuild_topics(n_topics: int = 10) -> dict:
    """Rebuild topic model from scratch."""
    with sync_session_factory() as db:
        # Get completed books
        result = db.execute(
            select(Book.id).where(Book.processing_status == "completed")
        )
        book_ids = [r[0] for r in result.all()]

        if len(book_ids) < 3:
            return {"error": "Not enough books for topic modeling"}

        n_topics = min(n_topics, max(2, len(book_ids) // 2))

        # Get average embedding per book
        book_embeddings = []
        valid_ids = []

        for bid in book_ids:
            chunks = db.execute(
                select(BookChunk.embedding)
                .where(BookChunk.book_id == bid)
                .where(BookChunk.embedding.isnot(None))
                .limit(20)
            ).all()

            embeddings = [r[0] for r in chunks if r[0] is not None]
            if embeddings:
                avg = np.mean(embeddings, axis=0)
                book_embeddings.append(avg)
                valid_ids.append(bid)

        if len(book_embeddings) < 2:
            return {"error": "Not enough embeddings"}

        X = np.array(book_embeddings)
        kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        # Clear old topics
        db.execute(delete(BookTopic))
        db.execute(delete(TopicRelation))
        db.execute(delete(Topic))
        db.flush()

        topics_created = 0
        topic_objects = []

        for i in range(n_topics):
            cluster_books = [valid_ids[j] for j in range(len(labels)) if labels[j] == i]
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
            db.flush()

            topic_objects.append(topic)

            for bid in cluster_books:
                bt = BookTopic(book_id=bid, topic_id=topic.id, relevance=0.8)
                db.add(bt)

            topics_created += 1

        # Create topic relations
        for i, ta in enumerate(topic_objects):
            for j, tb in enumerate(topic_objects):
                if i >= j:
                    continue
                if ta.embedding and tb.embedding:
                    similarity = float(np.dot(ta.embedding, tb.embedding) / (
                        np.linalg.norm(ta.embedding) * np.linalg.norm(tb.embedding) + 1e-8
                    ))
                    if similarity > 0.3:
                        rel = TopicRelation(
                            topic_a_id=ta.id,
                            topic_b_id=tb.id,
                            strength=similarity,
                            relation_type="related",
                        )
                        db.add(rel)

        db.commit()
        return {"topics_created": topics_created}
