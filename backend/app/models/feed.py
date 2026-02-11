from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from app.db.base import Base
import datetime


class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String(50), nullable=False, index=True)
    # til, connection, quote, concept, recommendation, milestone, daily_digest
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    book_ids = Column(ARRAY(Integer), default=[])
    metadata_json = Column(JSONB, default={})
    is_read = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
