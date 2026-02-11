"""Topic endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import topic_service
from app.schemas.topic import TopicOut, TopicGraphResponse

router = APIRouter()


@router.get("", response_model=list[TopicOut])
async def list_topics(db: AsyncSession = Depends(get_async_session)):
    topics = await topic_service.get_topics(db)
    return [TopicOut.model_validate(t) for t in topics]


@router.get("/graph", response_model=TopicGraphResponse)
async def topic_graph(db: AsyncSession = Depends(get_async_session)):
    graph = await topic_service.get_topic_graph(db)
    return TopicGraphResponse(**graph)


@router.get("/{topic_id}")
async def get_topic(topic_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await topic_service.get_topic_with_books(db, topic_id)
    if not result:
        raise HTTPException(status_code=404, detail="Topic not found")

    from app.schemas.book import BookOut
    return {
        "topic": TopicOut.model_validate(result["topic"]),
        "books": [BookOut.model_validate(b) for b in result["books"]],
    }
