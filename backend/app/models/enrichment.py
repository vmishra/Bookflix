from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
import datetime


class ExternalMetadata(Base):
    __tablename__ = "external_metadata"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # google_books, open_library
    external_id = Column(String(200))
    raw_data = Column(JSONB, default={})

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="external_metadata")
