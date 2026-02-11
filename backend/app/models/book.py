from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.db.base import Base
import datetime


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(500), index=True)
    isbn = Column(String(20))
    description = Column(Text)
    publisher = Column(String(300))
    published_date = Column(String(50))
    language = Column(String(10), default="en")
    page_count = Column(Integer)
    file_hash = Column(String(64), unique=True, nullable=False, index=True)
    cover_path = Column(String(500))
    processing_status = Column(String(20), default="pending", index=True)
    # pending, scanning, extracting, chunking, embedding, generating_insights, completed, failed
    processing_progress = Column(Float, default=0.0)
    rating = Column(Float)  # from external APIs
    search_vector = Column(TSVECTOR)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    files = relationship("BookFile", back_populates="book", cascade="all, delete-orphan")
    chunks = relationship("BookChunk", back_populates="book", cascade="all, delete-orphan")
    insights = relationship("BookInsight", back_populates="book", cascade="all, delete-orphan")
    categories = relationship("BookCategory", back_populates="book", cascade="all, delete-orphan")
    tags = relationship("BookTag", back_populates="book", cascade="all, delete-orphan")
    topics = relationship("BookTopic", back_populates="book", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="book", uselist=False, cascade="all, delete-orphan")
    reading_sessions = relationship("ReadingSession", back_populates="book", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="book", cascade="all, delete-orphan")
    external_metadata = relationship("ExternalMetadata", back_populates="book", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_books_search_vector", "search_vector", postgresql_using="gin"),
    )


class BookFile(Base):
    __tablename__ = "book_files"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1000), unique=True, nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, epub
    file_size = Column(Integer)  # bytes
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="files")
