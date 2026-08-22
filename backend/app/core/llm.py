import httpx

from app.core.config import settings

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class LLMNotConfigured(Exception):
    pass


def is_configured() -> bool:
    return bool(settings.LLM_API_KEY)


def send_chat(messages: list[dict[str, str]], system_prompt: str) -> str:
    """messages: [{"role": "user"|"assistant", "content": str}, ...], oldest
    first. Raises LLMNotConfigured if no API key is set, or
    httpx.HTTPStatusError/httpx.HTTPError on a provider-side failure —
    callers are expected to catch and translate those into a friendly
    AppError rather than let them bubble up raw."""
    if not is_configured():
        raise LLMNotConfigured()

    response = httpx.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": settings.LLM_API_KEY,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        json={
            "model": settings.LLM_MODEL,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": messages,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return "".join(block["text"] for block in data["content"] if block["type"] == "text")
