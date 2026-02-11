"""AI insight generation tasks."""
import json
import logging
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.models.book import Book
from app.models.chunk import BookChunk
from app.models.insight import BookInsight
from app.models.processing import ProcessingJob
from app.processing.embedder import generate_single_embedding
from sqlalchemy import select
import datetime

logger = logging.getLogger(__name__)


def _sync_llm_call(messages: list[dict], task_type: str = "insight") -> str:
    """Synchronous LLM call for Celery workers."""
    from openai import OpenAI
    from app.config import settings

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    response = client.chat.completions.create(
        model=settings.default_model,
        messages=messages,
        temperature=0.7,
        max_tokens=4096,
    )
    return response.choices[0].message.content or ""


@celery_app.task(name="celery_app.tasks.insight_tasks.generate_book_insights", bind=True)
def generate_book_insights(self, book_id: int, pass_level: int = 1) -> dict:
    """Generate AI insights for a book."""
    from app.llm.prompts import SYSTEM_INSIGHT, EXTRACT_KEY_CONCEPTS, EXTRACT_FRAMEWORKS, EXTRACT_TAKEAWAYS

    with sync_session_factory() as db:
        book = db.get(Book, book_id)
        if not book:
            return {"error": "Book not found"}

        book.processing_status = "generating_insights"

        stage = f"insights_pass_{pass_level}"
        job = db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.book_id == book_id)
            .where(ProcessingJob.stage == stage)
        ).scalar_one_or_none()

        if not job:
            job = ProcessingJob(book_id=book_id, stage=stage, status="pending")
            db.add(job)

        job.status = "running"
        job.celery_task_id = self.request.id
        job.started_at = datetime.datetime.utcnow()
        job.attempts += 1
        db.commit()

        try:
            chunk_limit = 20 if pass_level == 1 else 50
            chunks = db.execute(
                select(BookChunk)
                .where(BookChunk.book_id == book_id)
                .order_by(BookChunk.chunk_index)
                .limit(chunk_limit)
            ).scalars().all()

            if not chunks:
                job.status = "skipped"
                db.commit()
                return {"book_id": book_id, "insights": 0}

            content = "\n\n---\n\n".join(c.content for c in chunks)
            insights_count = 0

            # Extract key concepts
            try:
                response = _sync_llm_call(
                    messages=[
                        {"role": "system", "content": SYSTEM_INSIGHT},
                        {"role": "user", "content": EXTRACT_KEY_CONCEPTS.format(
                            title=book.title, author=book.author or "Unknown", content=content[:50000]
                        )},
                    ],
                )
                data = json.loads(response)
                for concept in data.get("concepts", []):
                    embedding = generate_single_embedding(f"{concept['title']}: {concept['content']}")
                    insight = BookInsight(
                        book_id=book_id,
                        insight_type="key_concept",
                        title=concept["title"],
                        content=concept["content"],
                        supporting_quote=concept.get("supporting_quote"),
                        importance=concept.get("importance", 5),
                        refinement_level=pass_level,
                        embedding=embedding,
                    )
                    db.add(insight)
                    insights_count += 1
            except Exception as e:
                logger.error(f"Concept extraction failed: {e}")

            # Extract frameworks
            try:
                response = _sync_llm_call(
                    messages=[
                        {"role": "system", "content": SYSTEM_INSIGHT},
                        {"role": "user", "content": EXTRACT_FRAMEWORKS.format(
                            title=book.title, author=book.author or "Unknown", content=content[:50000]
                        )},
                    ],
                )
                data = json.loads(response)
                for fw in data.get("frameworks", []):
                    embedding = generate_single_embedding(f"{fw['title']}: {fw['content']}")
                    insight = BookInsight(
                        book_id=book_id,
                        insight_type="framework",
                        title=fw["title"],
                        content=fw["content"],
                        supporting_quote=fw.get("supporting_quote"),
                        importance=fw.get("importance", 5),
                        refinement_level=pass_level,
                        embedding=embedding,
                    )
                    db.add(insight)
                    insights_count += 1
            except Exception as e:
                logger.error(f"Framework extraction failed: {e}")

            # Extract takeaways
            try:
                response = _sync_llm_call(
                    messages=[
                        {"role": "system", "content": SYSTEM_INSIGHT},
                        {"role": "user", "content": EXTRACT_TAKEAWAYS.format(
                            title=book.title, author=book.author or "Unknown", content=content[:50000]
                        )},
                    ],
                )
                data = json.loads(response)
                for tw in data.get("takeaways", []):
                    embedding = generate_single_embedding(f"{tw['title']}: {tw['content']}")
                    insight = BookInsight(
                        book_id=book_id,
                        insight_type="takeaway",
                        title=tw["title"],
                        content=tw["content"],
                        importance=tw.get("importance", 5),
                        refinement_level=pass_level,
                        embedding=embedding,
                    )
                    db.add(insight)
                    insights_count += 1
            except Exception as e:
                logger.error(f"Takeaway extraction failed: {e}")

            book.processing_status = "completed"
            book.processing_progress = 100.0
            job.status = "completed"
            job.completed_at = datetime.datetime.utcnow()
            db.commit()

            # Trigger enrichment
            from celery_app.tasks.enrichment_tasks import enrich_book
            enrich_book.delay(book_id)

            return {"book_id": book_id, "insights": insights_count, "pass_level": pass_level}

        except Exception as e:
            logger.error(f"Insight generation failed for book {book_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
            return {"error": str(e)}
