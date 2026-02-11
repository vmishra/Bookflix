"""Master API router."""
from fastapi import APIRouter
from app.api.v1 import books, library, search, insights, chat, feed, topics, recommendations, reading, knowledge, config

api_router = APIRouter()

api_router.include_router(library.router, prefix="/v1/library", tags=["library"])
api_router.include_router(books.router, prefix="/v1/books", tags=["books"])
api_router.include_router(search.router, prefix="/v1/search", tags=["search"])
api_router.include_router(insights.router, prefix="/v1/insights", tags=["insights"])
api_router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
api_router.include_router(feed.router, prefix="/v1/feed", tags=["feed"])
api_router.include_router(topics.router, prefix="/v1/topics", tags=["topics"])
api_router.include_router(recommendations.router, prefix="/v1/recommendations", tags=["recommendations"])
api_router.include_router(reading.router, prefix="/v1/reading", tags=["reading"])
api_router.include_router(knowledge.router, prefix="/v1/knowledge", tags=["knowledge"])
api_router.include_router(config.router, prefix="/v1/config", tags=["config"])
