from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from app.db.base import Base
import datetime


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    keywords = Column(ARRAY(String))
    embedding = Column(Vector(384))
    book_count = Column(Integer, default=0)
    color = Column(String(7))  # hex color for UI

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    books = relationship("BookTopic", back_populates="topic")


class BookTopic(Base):
    __tablename__ = "book_topics"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    relevance = Column(Float, default=0.5)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="topics")
    topic = relationship("Topic", back_populates="books")


class TopicRelation(Base):
    __tablename__ = "topic_relations"

    id = Column(Integer, primary_key=True, index=True)
    topic_a_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    topic_b_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    strength = Column(Float, default=0.0)
    relation_type = Column(String(50))  # related, subtopic, overlapping

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    topic_a = relationship("Topic", foreign_keys=[topic_a_id])
    topic_b = relationship("Topic", foreign_keys=[topic_b_id])
