from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.finral.agent import finral_agent
from app.agents.noelle.agent import noelle_agent
from app.agents.yami.agent import yami_agent
from app.graph.nodes.memory_node import extract_memory_node, load_memory_node


class AgentState(TypedDict):
    user_input: str
    response: str
    next_agent: Optional[str]
    # ---- Memory fields ----
    user_id: str  # Per-user memory lookup
    session_id: str  # Conversation continuity
    current_agent: str  # Which agent is executing (for namespace)
    memory_context: str  # Formatted memory text to inject into prompt
    messages: List[Dict[str, str]]  # Accumulated conversation history
    agent_memory: Dict[str, Any]  # Ephemeral working memory
    retrieved_context: List[str]  # Top-K semantically retrieved snippets
    extracted_memories: List[Dict[str, str]]  # New facts persisted this turn


def route_to_subagent(state: AgentState):
    """
    Supervisor routing logic. Determines which node LangGraph transitions to next.
    """
    next_agent = state.get("next_agent", "END")
    if next_agent in ["finral", "noelle"]:
        # Set current_agent so memory node knows whose namespace to use
        state["current_agent"] = next_agent
        return next_agent
    return "END"


workflow = StateGraph(AgentState)

# ---- Memory nodes ----
workflow.add_node("load_memory", load_memory_node)
workflow.add_node("extract_memory", extract_memory_node)

# ---- Agent nodes ----
workflow.add_node("yami", yami_agent)
workflow.add_node("finral", finral_agent)
workflow.add_node("noelle", noelle_agent)

# ---- Graph flow: Load memories → Yami → (sub-agent | END) → Extract memories ----
workflow.set_entry_point("load_memory")

# After loading memories, route to Yami (the supervisor)
workflow.add_edge("load_memory", "yami")

# After Yami, conditionally route to Finral, Noelle, or END
workflow.add_conditional_edges(
    "yami",
    route_to_subagent,
    {
        "finral": "finral",
        "noelle": "noelle",
        "END": "extract_memory",
    },
)

# Sub-agents complete their task, then we extract & persist memories
workflow.add_edge("finral", "extract_memory")
workflow.add_edge("noelle", "extract_memory")

# After extracting memories, the graph ends
workflow.add_edge("extract_memory", END)

graph = workflow.compile()
