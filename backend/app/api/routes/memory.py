from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config.database import get_session
from app.memory.postgres.memory_store import memory_store
from app.memory.vector.embedding_service import embedding_service

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryCreate(BaseModel):
    key: str
    value: str
    agent_name: Optional[str] = "shared"


@router.get("/{user_id}")
async def get_all_memories(
    user_id: str,
    agent_name: Optional[str] = Query(None, description="Filter memories by agent"),
    session: Optional[AsyncSession] = Depends(get_session),
):
    """Retrieve all memories stored for a specific user ID."""
    try:
        memories = await memory_store.get_all(session, user_id, agent_name=agent_name)
        # Convert dictionary to a nice list structure for the UI
        return [
            {"key": k, "value": v, "agent_name": agent_name or "shared"}
            for k, v in memories.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}")
async def upsert_memory(
    user_id: str,
    req: MemoryCreate,
    session: Optional[AsyncSession] = Depends(get_session),
):
    """Upsert (create or update) a memory entry for the given user."""
    try:
        # Generate embedding if embedding service is active
        embedding = None
        if embedding_service.is_available():
            embedding = await embedding_service.embed_text(req.value)

        await memory_store.store(
            session,
            user_id=user_id,
            key=req.key,
            value=req.value,
            agent_name=req.agent_name or "shared",
            embedding=embedding,
        )
        return {"status": "success", "message": f"Memory stored for {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/{key}")
async def delete_memory(
    user_id: str,
    key: str,
    session: Optional[AsyncSession] = Depends(get_session),
):
    """Delete a specific memory key for a user."""
    try:
        deleted = await memory_store.delete(session, user_id, key)
        if not deleted:
            raise HTTPException(status_code=404, detail="Memory key not found")
        return {"status": "success", "message": f"Memory key '{key}' deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def clear_all_memories(
    user_id: str,
    session: Optional[AsyncSession] = Depends(get_session),
):
    """Clear all memories for a user."""
    try:
        await memory_store.clear(session, user_id)
        return {"status": "success", "message": f"All memories cleared for {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
