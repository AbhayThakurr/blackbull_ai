"""Initialize the database — create tables and extensions.

Usage:
    python -m app.scripts.init_db

Requires DATABASE_URL in your .env pointing to a running PostgreSQL instance
with the pgvector extension available.
"""

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.database import _convert_to_async_url
from app.config.settings import settings
from app.models.memory import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def init():
    async_url = _convert_to_async_url(settings.DATABASE_URL)
    engine = create_async_engine(async_url, echo=True)

    async with engine.connect() as conn:
        # Enable pgvector extension (required for Vector column type)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.commit()

        # Create all tables defined in Base (UserMemory, Conversation, Message)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    logger.info("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init())
