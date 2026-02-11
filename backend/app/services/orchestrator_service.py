"""Autonomous agent brain - coordinates all background processing."""
import logging
import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.processing import ProcessingJob
from app.models.insight import BookInsight
from app.models.feed import FeedItem
from app.config import settings

logger = logging.getLogger(__name__)

INTENSITY_CONFIG = {
    "aggressive": {"tick_interval": 60, "max_concurrent": 5},
    "normal": {"tick_interval": 300, "max_concurrent": 2},
    "idle": {"tick_interval": 1800, "max_concurrent": 1},
    "paused": {"tick_interval": None, "max_concurrent": 0},
}


class OrchestratorBrain:
    def __init__(self, db: Session):
        self.db = db
        self.intensity = settings.orchestrator_intensity

    def get_next_action(self) -> dict | None:
        """Determine the highest-priority action to take."""
        if self.intensity == "paused":
            return None

        # Priority 1: Unprocessed books
        action = self._check_new_books()
        if action:
            return action

        # Priority 2: Partially processed books
        action = self._check_incomplete_books()
        if action:
            return action

        # Priority 3: Books needing insight refinement
        action = self._check_shallow_insights()
        if action:
            return action

        # Priority 4: Feed generation
        action = self._check_feed_needs()
        if action:
            return action

        # Priority 5: Enrichment gaps
        action = self._check_enrichment_gaps()
        if action:
            return action

        return None

    def _check_new_books(self) -> dict | None:
        result = self.db.execute(
            select(Book)
            .where(Book.processing_status == "pending")
            .order_by(Book.created_at)
            .limit(1)
        )
        book = result.scalar_one_or_none()
        if book:
            return {"action": "process_book", "book_id": book.id, "priority": 1}
        return None

    def _check_incomplete_books(self) -> dict | None:
        result = self.db.execute(
            select(Book)
            .where(Book.processing_status.in_(["extracting", "chunking", "embedding"]))
            .order_by(Book.updated_at)
            .limit(1)
        )
        book = result.scalar_one_or_none()
        if book:
            return {"action": "resume_processing", "book_id": book.id, "priority": 2}
        return None

    def _check_shallow_insights(self) -> dict | None:
        subquery = (
            select(BookInsight.book_id, func.max(BookInsight.refinement_level).label("max_level"))
            .group_by(BookInsight.book_id)
            .subquery()
        )
        result = self.db.execute(
            select(Book)
            .join(subquery, Book.id == subquery.c.book_id)
            .where(subquery.c.max_level < 3)
            .where(Book.processing_status == "completed")
            .limit(1)
        )
        book = result.scalar_one_or_none()
        if book:
            return {"action": "refine_insights", "book_id": book.id, "priority": 3}
        return None

    def _check_feed_needs(self) -> dict | None:
        unread = self.db.scalar(
            select(func.count(FeedItem.id)).where(FeedItem.is_read.is_(False))
        ) or 0
        if unread < 5:
            return {"action": "generate_feed", "priority": 4}
        return None

    def _check_enrichment_gaps(self) -> dict | None:
        result = self.db.execute(
            select(Book)
            .where(Book.description.is_(None))
            .where(Book.processing_status == "completed")
            .limit(1)
        )
        book = result.scalar_one_or_none()
        if book:
            return {"action": "enrich_book", "book_id": book.id, "priority": 5}
        return None
