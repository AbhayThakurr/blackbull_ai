import os
import re

from langchain.agents import create_agent
from langchain.tools import tool

from app.llm.bedrock import get_nova_micro
from app.tools.system.system_tools import (
    change_system_wallpaper,
    list_installed_apps,
    open_system_app,
)


@tool
def delegate_to_finral(task_description: str) -> str:
    """
    Delegates browser navigation, web searches, and portal tasks to Finral Roulacase.
    Use this tool when the user asks to search the web, open a URL,
    or find something online (e.g. 'search for netflix').
    """
    return f"ROUTING_TO:finral|{task_description}"


@tool
def delegate_to_noelle(task_description: str) -> str:
    """
    Delegates calendar, meeting checks, Google Meet scheduling, launching/opening
    meetings, email tasks, and Google Calendar reauthentication to Noelle Silva.
    Use this tool when the user asks about upcoming meetings, Google Meets,
    calendar events, scheduling meetings, opening meeting links, sending email notifications,
    or reauthenticating/refreshing their Google Calendar access.
    """
    return f"ROUTING_TO:noelle|{task_description}"


def load_skills() -> str:
    skills_path = os.path.join(os.path.dirname(__file__), "skills.md")
    with open(skills_path, "r") as f:
        return f.read()


# Define Yami using the unified create_agent method
yami_runnable = create_agent(
    model=get_nova_micro(),
    tools=[
        open_system_app,
        list_installed_apps,
        change_system_wallpaper,
        delegate_to_finral,
        delegate_to_noelle,
    ],
    system_prompt=load_skills(),
)


def _build_yami_prompt(state: dict) -> str:
    """Build an enriched system prompt that includes memory context."""
    base_prompt = load_skills()
    memory_context = state.get("memory_context", "")

    if memory_context:
        return f"{base_prompt}\n\n---\n# User Context (from memory)\n\n{memory_context}"
    return base_prompt


def yami_agent(state: dict):
    """
    Wrapper to bridge our graph state with the create_agent runnable.

    Acts as the Supervisor / Router for BlackBull AI.
    Receives enriched state with conversation history and memory context.
    """
    user_input = state.get("user_input", "")
    messages = state.get("messages", [])

    # Build enriched system prompt with memory context
    enriched_prompt = _build_yami_prompt(state)

    # Re-create the runnable with the enriched prompt for this invocation.
    # (create_agent is lightweight; this ensures fresh prompt per call.)
    runnable = create_agent(
        model=get_nova_micro(),
        tools=[
            open_system_app,
            list_installed_apps,
            change_system_wallpaper,
            delegate_to_finral,
            delegate_to_noelle,
        ],
        system_prompt=enriched_prompt,
    )

    # Pass conversation history + current user input
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
        clean_content = "Task completed successfully by Captain Yami."

    # Check tool messages for routing instructions
    next_agent = "END"
    new_input = user_input

    for msg in result["messages"]:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if "ROUTING_TO:finral" in msg.content:
                next_agent = "finral"
                parts = msg.content.split("|", 1)
                if len(parts) > 1:
                    new_input = parts[1]
                break
            elif "ROUTING_TO:noelle" in msg.content:
                next_agent = "noelle"
                parts = msg.content.split("|", 1)
                if len(parts) > 1:
                    new_input = parts[1]
                break

    return {
        "response": (
            clean_content
            if next_agent == "END"
            else f"Captain Yami delegating task to {next_agent.capitalize()}..."
        ),
        "user_input": new_input,
        "next_agent": next_agent,
        "current_agent": "yami",
    }
