from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"))
    is_auto = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    topic = relationship("Topic")
    books = relationship("LearningPathBook", back_populates="path", cascade="all, delete-orphan", order_by="LearningPathBook.position")


class LearningPathBook(Base):
    __tablename__ = "learning_path_books"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    rationale = Column(Text)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    path = relationship("LearningPath", back_populates="books")
    book = relationship("Book")
