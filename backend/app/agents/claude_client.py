"""
Thin wrapper around the Anthropic API. If ANTHROPIC_API_KEY=mock,
returns the caller-supplied mock response instead of making a real call.
"""
import json
import re

from app.core.config import get_settings

settings = get_settings()
_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
    return text


def call_claude_json(system_prompt: str, user_prompt: str, mock_response: dict, max_tokens: int = 1000) -> dict:
    if settings.claude_is_mocked:
        return mock_response

    client = _get_client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    cleaned = _strip_json_fences(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Could not parse Claude response", "raw": raw_text}


def call_claude_text(
    system_prompt: str, user_prompt: str, mock_response: str,
    max_tokens: int = 600, conversation_history: list = None,
) -> str:
    if settings.claude_is_mocked:
        return mock_response

    client = _get_client()
    messages = list(conversation_history) if conversation_history else []
    messages.append({"role": "user", "content": user_prompt})

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    return "".join(block.text for block in response.content if block.type == "text")
