"""Async PostgreSQL database engine and session factory."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.memory import Base

logger = logging.getLogger(__name__)

# Replace postgresql:// with postgresql+asyncpg:// for async support
_engine = None
_async_session_factory = None


def _convert_to_async_url(database_url: str) -> str:
    """Convert a sync database URL to asyncpg-compatible format."""
    if "postgresql+asyncpg" in database_url:
        return database_url
    return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)


def get_engine():
    """Lazily create and return the async engine."""
    global _engine, _async_session_factory
    if _engine is None:
        from app.config.settings import settings

        try:
            async_url = _convert_to_async_url(settings.DATABASE_URL)
            _engine = create_async_engine(async_url, echo=False, pool_size=5)
            _async_session_factory = async_sessionmaker(
                _engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info("Database engine created successfully.")
        except Exception as e:
            logger.warning(
                f"Could not create database engine: {e}. "
                "Memory will operate in ephemeral mode."
            )
            _engine = None
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield an async database session."""
    engine = get_engine()
    if engine is None:
        # If no database is available, yield None so callers can fallback
        yield None
        return

    async with _async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def create_session():
    """Create a new async session directly (not as a FastAPI dependency).

    Returns None if the database engine couldn't be initialized.
    """
    engine = get_engine()
    if engine is None or _async_session_factory is None:
        return None
    return _async_session_factory()
