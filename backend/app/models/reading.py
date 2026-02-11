from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime


class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_page = Column(Integer, default=0)
    total_pages = Column(Integer)
    progress_percent = Column(Float, default=0.0)
    status = Column(String(20), default="not_started")  # not_started, reading, completed, abandoned
    total_read_time = Column(Integer, default=0)  # seconds
    last_read_at = Column(DateTime)
    epub_cfi = Column(String(500))  # EPUB location

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="reading_progress")


class ReadingSession(Base):
    __tablename__ = "reading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime)
    pages_read = Column(Integer, default=0)
    duration = Column(Integer)  # seconds

    book = relationship("Book", back_populates="reading_sessions")
