"""Autonomous orchestrator agent tasks."""
import logging
from celery_app.celery import celery_app
from app.db.session import sync_session_factory
from app.services.orchestrator_service import OrchestratorBrain

logger = logging.getLogger(__name__)


@celery_app.task(name="celery_app.tasks.orchestrator_tasks.orchestrator_tick")
def orchestrator_tick() -> dict:
    """Main orchestrator tick - runs periodically via Beat."""
    with sync_session_factory() as db:
        brain = OrchestratorBrain(db)
        action = brain.get_next_action()

        if not action:
            return {"status": "idle", "message": "No actions needed"}

        logger.info(f"Orchestrator action: {action}")

        try:
            if action["action"] == "process_book":
                from celery_app.tasks.book_tasks import process_book
                process_book.delay(action["book_id"])
                return {"status": "dispatched", "action": "process_book", "book_id": action["book_id"]}

            elif action["action"] == "resume_processing":
                from celery_app.tasks.book_tasks import extract_text
                extract_text.delay(action["book_id"])
                return {"status": "dispatched", "action": "resume_processing", "book_id": action["book_id"]}

            elif action["action"] == "refine_insights":
                from celery_app.tasks.insight_tasks import generate_book_insights
                generate_book_insights.delay(action["book_id"], pass_level=2)
                return {"status": "dispatched", "action": "refine_insights", "book_id": action["book_id"]}

            elif action["action"] == "generate_feed":
                from celery_app.tasks.feed_tasks import generate_daily_feed
                generate_daily_feed.delay()
                return {"status": "dispatched", "action": "generate_feed"}

            elif action["action"] == "enrich_book":
                from celery_app.tasks.enrichment_tasks import enrich_book
                enrich_book.delay(action["book_id"])
                return {"status": "dispatched", "action": "enrich_book", "book_id": action["book_id"]}

            else:
                return {"status": "unknown_action", "action": action}

        except Exception as e:
            logger.error(f"Orchestrator dispatch failed: {e}")
            return {"status": "error", "error": str(e)}
