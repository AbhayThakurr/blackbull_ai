"""Memory extraction — uses the LLM to extract facts from conversations.

After each agent response, we ask the LLM to reflect on the exchange and
produce structured key:value facts to persist for future reference.
"""

import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
Analyze this conversation and extract any new information that should be \
remembered about the user.

Return ONLY a JSON array of objects with "key" and "value" fields.
If there's nothing new to remember, return an empty array [].

Current known memories (do NOT re-extract these):
{known_memories}

Conversation:
{conversation}

Extracted facts (JSON array only):\
"""


def build_extraction_prompt(conversation: str, known_memories: dict[str, str]) -> str:
    """Build the extraction prompt with known memories and conversation."""
    known_lines = ""
    if known_memories:
        known_lines = "\n".join(f"  - {k}: {v}" for k, v in known_memories.items())
    else:
        known_lines = "  (none)"

    return EXTRACTION_PROMPT.format(
        known_memories=known_lines, conversation=conversation
    )


def parse_extraction_result(raw_output: str) -> list[dict[str, str]]:
    """Parse the LLM extraction response into a list of {key, value} dicts.

    Handles both pure JSON and JSON wrapped in markdown code fences.
    """
    raw = raw_output.strip()

    # Strip markdown code fences if present
    code_fence = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", raw, re.DOTALL)
    if code_fence:
        raw = code_fence.group(1).strip()

    # Find the first JSON array in the response
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [
                item
                for item in parsed
                if isinstance(item, dict) and "key" in item and "value" in item
            ]
    except json.JSONDecodeError:
        logger.warning("Failed to parse extraction response as JSON: %s", raw)

    return []


async def extract_memories_from_conversation(
    llm,
    conversation_text: str,
    known_memories: dict[str, str],
) -> list[dict[str, str]]:
    """Ask the LLM to extract new memory facts from a conversation turn.

    Args:
        llm: A LangChain-compatible chat model.
        conversation_text: The full conversation exchange to analyze.
        known_memories: Already-known memories to avoid re-extraction.

    Returns:
        A list of {key, value} dicts representing new facts to persist.
    """
    import asyncio

    prompt = build_extraction_prompt(conversation_text, known_memories)

    try:
        loop = asyncio.get_running_loop()

        def _invoke():
            response = llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)

        result_text = await loop.run_in_executor(None, _invoke)
        return parse_extraction_result(result_text)
    except Exception as e:
        logger.error("Memory extraction LLM call failed: %s", e)
        return []
