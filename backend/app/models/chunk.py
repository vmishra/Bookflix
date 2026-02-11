from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from app.db.base import Base
import datetime


class BookChunk(Base):
    __tablename__ = "book_chunks"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    chapter = Column(String(300))
    token_count = Column(Integer)
    embedding = Column(Vector(384))
    search_vector = Column(TSVECTOR)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="chunks")

    __table_args__ = (
        Index("ix_book_chunks_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_book_chunks_embedding", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )
