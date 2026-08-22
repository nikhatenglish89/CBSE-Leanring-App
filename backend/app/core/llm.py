import httpx

from app.core.config import settings

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


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

    if settings.LLM_PROVIDER == "anthropic":
        return _send_chat_anthropic(messages, system_prompt)
    return _send_chat_gemini(messages, system_prompt)


def _send_chat_anthropic(messages: list[dict[str, str]], system_prompt: str) -> str:
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


def _send_chat_gemini(messages: list[dict[str, str]], system_prompt: str) -> str:
    # Gemini uses "model" (not "assistant") for the AI's own turns.
    contents = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
        for m in messages
    ]
    response = httpx.post(
        GEMINI_API_URL.format(model=settings.LLM_MODEL),
        params={"key": settings.LLM_API_KEY},
        json={
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"maxOutputTokens": 1024},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(part.get("text", "") for part in parts)
