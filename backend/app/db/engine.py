from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import create_engine, Engine
from app.config import settings

async_engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
)

sync_engine: Engine = create_engine(
    settings.database_url_sync,
    echo=False,
    pool_size=10,
    max_overflow=5,
)
