"""Celery instance and configuration."""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "bookflix",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "celery_app.tasks.book_tasks.*": {"queue": "processing"},
        "celery_app.tasks.embedding_tasks.*": {"queue": "embedding"},
        "celery_app.tasks.insight_tasks.*": {"queue": "llm"},
        "celery_app.tasks.enrichment_tasks.*": {"queue": "llm"},
        "celery_app.tasks.topic_tasks.*": {"queue": "llm"},
        "celery_app.tasks.feed_tasks.*": {"queue": "llm"},
        "celery_app.tasks.orchestrator_tasks.*": {"queue": "processing"},
    },
    beat_schedule={},  # Populated from schedules.py
)

# Import schedules
from celery_app.schedules import setup_beat_schedule
setup_beat_schedule(celery_app)

# Autodiscover tasks
celery_app.autodiscover_tasks(["celery_app.tasks"])
