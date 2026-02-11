from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base
import datetime


class BookInsight(Base):
    __tablename__ = "book_insights"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    insight_type = Column(String(50), nullable=False, index=True)
    # key_concept, mental_model, framework, takeaway, argument, quote, definition
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    supporting_quote = Column(Text)
    importance = Column(Integer, default=5)  # 1-10
    refinement_level = Column(Integer, default=1)
    embedding = Column(Vector(384))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="insights")

    __table_args__ = (
        Index("ix_book_insights_embedding", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class InsightConnection(Base):
    __tablename__ = "insight_connections"

    id = Column(Integer, primary_key=True, index=True)
    insight_a_id = Column(Integer, ForeignKey("book_insights.id", ondelete="CASCADE"), nullable=False)
    insight_b_id = Column(Integer, ForeignKey("book_insights.id", ondelete="CASCADE"), nullable=False)
    connection_type = Column(String(50))  # supports, contradicts, extends, similar
    strength = Column(Float, default=0.0)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    insight_a = relationship("BookInsight", foreign_keys=[insight_a_id])
    insight_b = relationship("BookInsight", foreign_keys=[insight_b_id])
