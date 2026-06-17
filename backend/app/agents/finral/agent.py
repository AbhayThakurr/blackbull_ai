import os
import re

from langchain.agents import create_agent

from app.llm.bedrock import get_nova_micro
from app.tools.browser.browser_tools import (
    open_url_in_browser,
    play_youtube_video,
    search_web_in_browser,
    search_youtube,
)


def load_skills() -> str:
    skills_path = os.path.join(os.path.dirname(__file__), "skills.md")
    with open(skills_path, "r") as f:
        return f.read()


def _build_finral_prompt(state: dict) -> str:
    """Build an enriched system prompt that includes memory context."""
    base_prompt = load_skills()
    memory_context = state.get("memory_context", "")

    if memory_context:
        return f"{base_prompt}\n\n---\n# User Context (from memory)\n\n{memory_context}"
    return base_prompt


def finral_agent(state: dict):
    """
    Executes Finral agent node to handle browser and web navigation tasks.

    Receives enriched state with conversation history and memory context.
    """
    user_input = state.get("user_input", "")
    messages = state.get("messages", [])

    # Build enriched system prompt with memory context
    enriched_prompt = _build_finral_prompt(state)

    runnable = create_agent(
        model=get_nova_micro(),
        tools=[
            search_web_in_browser,
            open_url_in_browser,
            search_youtube,
            play_youtube_video,
        ],
        system_prompt=enriched_prompt,
    )

    result = runnable.invoke(
        {
            "messages": [("user", msg["content"]) for msg in messages]
            + [("user", user_input)]
        }  # type: ignore[arg-type]
    )

    raw_content = result["messages"][-1].content
    clean_content = re.sub(
        r"<thinking>.*?</thinking>", "", raw_content, flags=re.DOTALL
    ).strip()
    if not clean_content:
        clean_content = "Task completed successfully by Finral."

    return {
        "response": clean_content,
        "next_agent": "END",
        "current_agent": "finral",
    }
