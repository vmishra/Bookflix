"""Celery Beat schedules."""
from celery.schedules import crontab


def setup_beat_schedule(app):
    app.conf.beat_schedule = {
        "orchestrator-tick": {
            "task": "celery_app.tasks.orchestrator_tasks.orchestrator_tick",
            "schedule": 300.0,  # 5 minutes
        },
        "daily-feed-generation": {
            "task": "celery_app.tasks.feed_tasks.generate_daily_feed",
            "schedule": crontab(hour=8, minute=0),
        },
        "weekly-topic-rebuild": {
            "task": "celery_app.tasks.topic_tasks.rebuild_topics",
            "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
        },
    }
