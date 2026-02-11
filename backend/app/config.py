from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://bookflix:bookflix_dev_password@db:5432/bookflix"
    database_url_sync: str = "postgresql+psycopg2://bookflix:bookflix_dev_password@db:5432/bookflix"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # OpenRouter
    openrouter_api_key: str = ""
    default_model: str = "stepfun/step-3.5-flash:free"

    # Paths
    books_path: str = "/books"
    covers_path: str = "/app/covers"

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Orchestrator
    orchestrator_intensity: str = "normal"
    orchestrator_tick_interval: int = 300

    # App
    secret_key: str = "change-me-to-random-string"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
