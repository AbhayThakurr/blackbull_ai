"""Semantic retrieval via pgvector cosine-similarity search."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.vector.embedding_service import embedding_service
from app.models.memory import UserMemory

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """Retrieves semantically relevant memories for a given user query.

    When pgvector + embeddings are available, performs cosine-similarity
    search. Falls back to full-text keyword matching when vectors aren't
    available.
    """

    TOP_K = 5

    async def retrieve(
        self,
        session: Optional[AsyncSession],
        user_id: str,
        query: str,
        agent_name: Optional[str] = None,
    ) -> dict[str, str]:
        """Return the top-K most relevant memories as {key: value}."""

        if session is None:
            logger.debug("No database session; skipping semantic retrieval.")
            return {}

        query_embedding = await embedding_service.embed_text(query)
        if query_embedding is None:
            return await self._keyword_retrieve(session, user_id, query, agent_name)

        return await self._vector_retrieve(
            session, user_id, query_embedding, agent_name
        )

    # ------------------------------------------------------------------
    # Vector-based retrieval (pgvector)
    # ------------------------------------------------------------------

    async def _vector_retrieve(
        self,
        session: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        agent_name: Optional[str],
    ) -> dict[str, str]:
        """Cosine-similarity search using pgvector's <=> operator."""
        stmt = (
            select(UserMemory.key, UserMemory.value)
            .where(UserMemory.user_id == user_id)
            .where(UserMemory.embedding.is_not(None))
            .order_by(UserMemory.embedding.cosine_distance(query_embedding))
            .limit(self.TOP_K)
        )
        if agent_name:
            stmt = stmt.where(UserMemory.agent_name == agent_name)

        result = await session.execute(stmt)
        rows = result.fetchall()
        return {row.key: row.value for row in rows}

    # ------------------------------------------------------------------
    # Keyword fallback
    # ------------------------------------------------------------------

    async def _keyword_retrieve(
        self,
        session: AsyncSession,
        user_id: str,
        query: str,
        agent_name: Optional[str],
    ) -> dict[str, str]:
        """Fallback: full-text ILIKE search when vectors aren't available."""
        stmt = (
            select(UserMemory.key, UserMemory.value)
            .where(UserMemory.user_id == user_id)
            .where(UserMemory.value.ilike(f"%{query}%"))
            .limit(self.TOP_K)
        )
        if agent_name:
            stmt = stmt.where(UserMemory.agent_name == agent_name)

        result = await session.execute(stmt)
        rows = result.fetchall()
        return {row.key: row.value for row in rows}


# Singleton instance
memory_retriever = MemoryRetriever()
