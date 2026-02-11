"""AI-generated social feed."""
import json
import logging
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.feed import FeedItem
from app.models.insight import BookInsight
from app.models.book import Book
from app.llm.client import llm_client
from app.llm.prompts import GENERATE_FEED_TIL, GENERATE_DAILY_QUOTE

logger = logging.getLogger(__name__)


async def get_feed(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
) -> tuple[list[FeedItem], int]:
    query = select(FeedItem)
    count_query = select(func.count(FeedItem.id))

    if unread_only:
        query = query.where(FeedItem.is_read.is_(False))
        count_query = count_query.where(FeedItem.is_read.is_(False))

    query = query.order_by(desc(FeedItem.is_pinned), desc(FeedItem.created_at))

    total = await db.scalar(count_query) or 0
    result = await db.execute(query.offset(skip).limit(limit))
    items = list(result.scalars().all())

    return items, total


async def generate_til_items(db: AsyncSession, limit: int = 3) -> list[FeedItem]:
    """Generate TIL feed items from recent insights."""
    result = await db.execute(
        select(BookInsight)
        .where(BookInsight.insight_type == "key_concept")
        .order_by(func.random())
        .limit(limit)
    )
    insights = result.scalars().all()
    items = []

    for insight in insights:
        book = await db.get(Book, insight.book_id)
        if not book:
            continue

        try:
            response = await llm_client.complete(
                messages=[{
                    "role": "user",
                    "content": GENERATE_FEED_TIL.format(
                        insight_title=insight.title,
                        insight_content=insight.content,
                        book_title=book.title,
                        author=book.author or "Unknown",
                    ),
                }],
                task_type="feed",
                max_tokens=500,
            )
            data = json.loads(response)
            item = FeedItem(
                item_type="til",
                title=data.get("title", f"TIL: {insight.title}"),
                content=data.get("content", insight.content),
                book_ids=[book.id],
                metadata_json={"insight_id": insight.id},
            )
            db.add(item)
            items.append(item)
        except Exception as e:
            logger.error(f"TIL generation failed: {e}")

    await db.flush()
    return items


async def mark_feed_read(db: AsyncSession, item_id: int) -> FeedItem | None:
    item = await db.get(FeedItem, item_id)
    if item:
        item.is_read = True
        await db.flush()
    return item


async def toggle_feed_pin(db: AsyncSession, item_id: int) -> FeedItem | None:
    item = await db.get(FeedItem, item_id)
    if item:
        item.is_pinned = not item.is_pinned
        await db.flush()
    return item
