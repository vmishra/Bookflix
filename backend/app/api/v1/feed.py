"""Feed endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import feed_service
from app.schemas.feed import FeedItemOut, FeedItemUpdate, FeedResponse
from app.models.feed import FeedItem
import datetime

router = APIRouter()


@router.get("", response_model=FeedResponse)
async def get_feed(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    db: AsyncSession = Depends(get_async_session),
):
    items, total = await feed_service.get_feed(db, skip=skip, limit=limit, unread_only=unread_only)
    unread = await db.scalar(
        select(func.count(FeedItem.id)).where(FeedItem.is_read.is_(False))
    ) or 0
    return FeedResponse(
        items=[FeedItemOut.model_validate(i) for i in items],
        total=total,
        unread_count=unread,
    )


@router.post("/generate")
async def generate_feed():
    from celery_app.tasks.feed_tasks import generate_daily_feed
    task = generate_daily_feed.delay()
    return {"task_id": task.id, "message": "Feed generation started"}


@router.patch("/{item_id}", response_model=FeedItemOut)
async def update_feed_item(
    item_id: int,
    update: FeedItemUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    item = await db.get(FeedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")

    if update.is_read is not None:
        item.is_read = update.is_read
    if update.is_pinned is not None:
        item.is_pinned = update.is_pinned
    await db.flush()
    return FeedItemOut.model_validate(item)


@router.get("/daily-digest")
async def daily_digest(db: AsyncSession = Depends(get_async_session)):
    today = datetime.date.today()
    result = await db.execute(
        select(FeedItem)
        .where(func.date(FeedItem.created_at) == today)
        .order_by(desc(FeedItem.created_at))
    )
    items = result.scalars().all()
    return {"date": str(today), "items": [FeedItemOut.model_validate(i) for i in items]}
