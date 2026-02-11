from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(String(500))
    parent_id = Column(Integer, ForeignKey("categories.id"))
    sort_order = Column(Integer, default=0)
    icon = Column(String(50))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    parent = relationship("Category", remote_side="Category.id", backref="children")
    books = relationship("BookCategory", back_populates="category")


class BookCategory(Base):
    __tablename__ = "book_categories"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    confidence = Column(Float, default=1.0)
    source = Column(String(20), default="ai")  # ai, manual, metadata

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="categories")
    category = relationship("Category", back_populates="books")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    usage_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    books = relationship("BookTag", back_populates="tag")


class BookTag(Base):
    __tablename__ = "book_tags"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="tags")
    tag = relationship("Tag", back_populates="books")
