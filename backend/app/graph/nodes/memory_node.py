"""LangGraph memory node — load, inject, extract, and persist memories.

This node is wired into the graph both *before* the Yami supervisor
(to inject context) and *after* sub-agent execution (to extract new facts).
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import create_session
from app.llm.bedrock import get_nova_micro
from app.memory.memory_extractor import extract_memories_from_conversation
from app.memory.postgres.memory_store import memory_store
from app.memory.retrieval.retriever import memory_retriever
from app.memory.vector.embedding_service import embedding_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pre-agent node: load past memories and inject as context
# ---------------------------------------------------------------------------


def _get_or_create_session() -> Optional[AsyncSession]:
    """Return a DB session if one is available; otherwise None."""
    try:
        return create_session()
    except Exception:
        return None


async def load_memory_node(state: dict) -> dict:
    """Load persistent + semantic memories and inject them into the state.

    This runs *before* Yami. It:
      1. Loads all known user memories from the DB (or fallback).
      2. Runs a semantic search for contextually relevant memories.
      3. Formats them into `memory_context` for prompt injection.
      4. Sets `session_id` if one isn't already present.

    Returns a partial state dict with the enriched fields.
    """
    user_id = state.get("user_id", "unknown")
    session_id = state.get("session_id") or str(uuid.uuid4())
    user_input = state.get("user_input", "")
    agent_name = state.get("current_agent", "yami")

    session = _get_or_create_session()

    # If no DB is available, skip memory loading entirely
    if session is None:
        messages = state.get("messages", [])
        if user_input.strip():
            messages.append({"role": "user", "content": user_input})
        return {
            "session_id": session_id,
            "memory_context": "",
            "messages": messages,
            "agent_memory": state.get("agent_memory", {}),
            "retrieved_context": [],
        }

    try:
        # 1. Load all known memories for this user + agent
        all_memories = await memory_store.get_all(
            session, user_id, agent_name=agent_name
        )

        # 2. Semantic retrieval for contextually relevant memories
        retrieved = {}
        if user_input.strip():
            retrieved = await memory_retriever.retrieve(
                session, user_id, user_input, agent_name=agent_name
            )

        # Merge: retrieved first, then all memories (dedup by key)
        merged = {**retrieved, **all_memories}

        # 3. Format for prompt injection
        memory_context = memory_store.format_for_prompt(merged, agent_name)

        # 4. Accumulate conversation history in messages
        messages = state.get("messages", [])
        if user_input.strip():
            messages.append({"role": "user", "content": user_input})

        return {
            "session_id": session_id,
            "memory_context": memory_context,
            "messages": messages,
            "agent_memory": state.get("agent_memory", {}),
            "retrieved_context": list(retrieved.values()),
        }

    finally:
        if session is not None:
            await session.close()


# ---------------------------------------------------------------------------
# Post-agent node: extract new facts and persist them
# ---------------------------------------------------------------------------


async def extract_memory_node(state: dict) -> dict:
    """Extract new facts from the exchange and persist to the memory store.

    This runs *after* a sub-agent has responded. It:
      1. Builds a conversation summary from `state["messages"]`.
      2. Calls the LLM to extract new {key, value} facts.
      3. Upserts each fact into the persistent memory store.
      4. Optionally embeds each fact for future semantic retrieval.

    Returns a partial state dict with `extracted_memories`.
    """
    user_id = state.get("user_id", "unknown")
    agent_name = state.get("current_agent", "yami")
    response_text = state.get("response", "")
    messages = state.get("messages", [])

    # Append the agent's response to the message history
    if response_text.strip():
        messages.append({"role": "assistant", "content": response_text})

    # Build a plain-text conversation block
    conversation_lines = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        conversation_lines.append(f"[{role}]: {content}")
    conversation_text = "\n".join(conversation_lines)

    session = _get_or_create_session()

    # If no DB is available, skip memory extraction entirely
    if session is None:
        return {
            "extracted_memories": [],
            "messages": messages,
        }

    try:
        known_memories = await memory_store.get_all(
            session, user_id, agent_name=agent_name
        )

        # Ask the LLM to extract new facts
        llm = get_nova_micro()
        extracted = await extract_memories_from_conversation(
            llm, conversation_text, known_memories
        )

        # Persist each extracted fact
        persisted = []
        for item in extracted:
            key = item.get("key", "").strip()
            value = item.get("value", "").strip()
            if not key or not value:
                continue

            # Generate embedding for semantic retrieval
            embedding = None
            if embedding_service.is_available():
                embedding = await embedding_service.embed_text(value)

            await memory_store.store(
                session,
                user_id=user_id,
                key=key,
                value=value,
                agent_name=agent_name,
                embedding=embedding,
            )
            persisted.append({"key": key, "value": value})

        logger.info(
            "Extracted %d new memories for user=%s agent=%s",
            len(persisted),
            user_id,
            agent_name,
        )

        return {
            "extracted_memories": persisted,
            "messages": messages,
        }

    finally:
        if session is not None:
            await session.close()
