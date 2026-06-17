"""CRUD operations for persistent agent/user memory."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import UserMemory

logger = logging.getLogger(__name__)


class MemoryStore:
    """Manages persistent key-value memories for users and agents.

    Provides in-memory fallback when PostgreSQL is unavailable, ensuring
    the agent can always function with at least ephemeral memory.
    """

    EPHEMERAL_MODE_WARNING = "MemoryStore operating in ephemeral mode."

    def __init__(self) -> None:
        self._fallback: dict[str, dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _memory_key(user_id: str, key: str) -> str:
        """Compose a unique key for the ephemeral fallback."""
        return f"{user_id}::{key}"

    async def _writable_session(
        self, session: Optional[AsyncSession]
    ) -> Optional[AsyncSession]:
        """Resolve a session or return None when write operations can't proceed."""
        if session is not None:
            return session
        logger.warning(
            "No database session available. Memory writes will be ephemeral."
        )
        return None

    # ------------------------------------------------------------------
    # Store / Update
    # ------------------------------------------------------------------

    async def store(
        self,
        session: Optional[AsyncSession],
        user_id: str,
        key: str,
        value: str,
        agent_name: str = "shared",
        embedding: Optional[list[float]] = None,
    ) -> None:
        """Upsert a memory entry for a given user and key."""
        if session is None:
            self._fallback[self._memory_key(user_id, key)] = value
            return

        stmt = (
            pg_insert(UserMemory)
            .values(
                user_id=user_id,
                agent_name=agent_name,
                key=key,
                value=value,
                embedding=embedding,
                updated_at=datetime.now(timezone.utc),
            )
            .on_conflict_do_update(
                index_elements=["user_id", "key"],
                set_={
                    "value": value,
                    "agent_name": agent_name,
                    "embedding": embedding,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
        )
        await session.execute(stmt)
        await session.commit()

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    async def get(
        self, session: Optional[AsyncSession], user_id: str, key: str
    ) -> Optional[str]:
        """Retrieve a single memory value by user and key."""
        if session is None:
            return self._fallback.get(self._memory_key(user_id, key))

        result = await session.execute(
            select(UserMemory.value).where(
                UserMemory.user_id == user_id, UserMemory.key == key
            )
        )
        row = result.scalar_one_or_none()
        return row

    async def get_all(
        self,
        session: Optional[AsyncSession],
        user_id: str,
        agent_name: Optional[str] = None,
    ) -> dict[str, str]:
        """Return all memories for a user, optionally filtered by agent."""
        if session is None:
            prefix = f"{user_id}::"
            return {
                k.removeprefix(prefix): v
                for k, v in self._fallback.items()
                if k.startswith(prefix)
            }

        stmt = select(UserMemory.key, UserMemory.value).where(
            UserMemory.user_id == user_id
        )
        if agent_name:
            stmt = stmt.where(UserMemory.agent_name == agent_name)

        result = await session.execute(stmt)
        return {row.key: row.value for row in result.fetchall()}

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete(
        self, session: Optional[AsyncSession], user_id: str, key: str
    ) -> bool:
        """Delete a single memory entry. Returns True if something was deleted."""
        if session is None:
            composed = self._memory_key(user_id, key)
            return self._fallback.pop(composed, None) is not None

        result = await session.execute(
            delete(UserMemory).where(
                UserMemory.user_id == user_id, UserMemory.key == key
            )
        )
        await session.commit()
        return result.rowcount > 0

    async def clear(self, session: Optional[AsyncSession], user_id: str) -> None:
        """Remove *all* memories for a user."""
        if session is None:
            prefix = f"{user_id}::"
            keys = [k for k in self._fallback if k.startswith(prefix)]
            for k in keys:
                del self._fallback[k]
            return

        await session.execute(delete(UserMemory).where(UserMemory.user_id == user_id))
        await session.commit()

    # ------------------------------------------------------------------
    # Formatting for prompt injection
    # ------------------------------------------------------------------

    def format_for_prompt(
        self, memories: dict[str, str], agent_name: Optional[str] = None
    ) -> str:
        """Format memories as a plain-text block suitable for system-prompt injection."""
        if not memories:
            return ""

        lines = ["## What I remember about you"]
        if agent_name:
            lines[0] += f" (for {agent_name})"
        lines.append("")

        for key, value in memories.items():
            lines.append(f"- **{key}**: {value}")

        return "\n".join(lines) + "\n"


# Singleton instance
memory_store = MemoryStore()
