"""Feed generation tasks."""
import json
import logging
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.models.book import Book
from app.models.insight import BookInsight
from app.models.feed import FeedItem
from sqlalchemy import select, func

logger = logging.getLogger(__name__)


def _sync_llm_call(messages: list[dict]) -> str:
    from openai import OpenAI
    from app.config import settings

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )
    response = client.chat.completions.create(
        model=settings.default_model,
        messages=messages,
        temperature=0.8,
        max_tokens=500,
    )
    return response.choices[0].message.content or ""


@celery_app.task(name="celery_app.tasks.feed_tasks.generate_daily_feed")
def generate_daily_feed() -> dict:
    """Generate daily feed items."""
    from app.llm.prompts import GENERATE_FEED_TIL

    with sync_session_factory() as db:
        items_created = 0

        # Generate TIL items
        insights = db.execute(
            select(BookInsight)
            .where(BookInsight.insight_type == "key_concept")
            .order_by(func.random())
            .limit(3)
        ).scalars().all()

        for insight in insights:
            book = db.get(Book, insight.book_id)
            if not book:
                continue

            try:
                response = _sync_llm_call([{
                    "role": "user",
                    "content": GENERATE_FEED_TIL.format(
                        insight_title=insight.title,
                        insight_content=insight.content,
                        book_title=book.title,
                        author=book.author or "Unknown",
                    ),
                }])
                data = json.loads(response)

                item = FeedItem(
                    item_type="til",
                    title=data.get("title", f"TIL: {insight.title}"),
                    content=data.get("content", insight.content),
                    book_ids=[book.id],
                    metadata_json={"insight_id": insight.id},
                )
                db.add(item)
                items_created += 1
            except Exception as e:
                logger.error(f"TIL generation failed: {e}")

        db.commit()
        return {"items_created": items_created}
