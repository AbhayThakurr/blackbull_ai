import uuid
from typing import Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel, Field

from app.graph.builder import graph

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = Field(
        default=None, description="Unique user identifier for memory"
    )


@router.post("/")
async def chat(
    req: ChatRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """
    Main chat endpoint that invokes the BlackBull AI LangGraph.

    Accepts an optional ``user_id`` in the body or ``X-User-Id`` header.
    When provided, persistent memories are loaded for that user and new
    facts are extracted and stored after the response.
    """
    user_id = req.user_id or x_user_id or "anonymous"
    session_id = str(uuid.uuid4())

    # Prepare the initial state for the graph
    initial_state = {
        "user_input": req.message,
        "response": "",
        "user_id": user_id,
        "session_id": session_id,
        "current_agent": "yami",
        "memory_context": "",
        "messages": [],
        "agent_memory": {},
        "retrieved_context": [],
        "extracted_memories": [],
    }

    # Invoke the graph asynchronously
    result = await graph.ainvoke(initial_state)

    return {
        "response": result.get("response", "Captain Yami is currently unavailable."),
        "session_id": result.get("session_id", session_id),
        "extracted_memories": result.get("extracted_memories", []),
    }
