from app.core import llm
from app.core.config import settings


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


def test_is_configured_false_without_key(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    assert llm.is_configured() is False


def test_is_configured_true_with_key(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "some-key")
    assert llm.is_configured() is True


def test_send_chat_raises_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    try:
        llm.send_chat([{"role": "user", "content": "hi"}], "system prompt")
        raise AssertionError("expected LLMNotConfigured")
    except llm.LLMNotConfigured:
        pass


def test_send_chat_gemini_builds_request_and_parses_reply(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "fake-gemini-key")
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "LLM_MODEL", "gemini-2.0-flash")

    captured = {}

    def fake_post(url, params=None, json=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        captured["json"] = json
        return _FakeResponse(
            {"candidates": [{"content": {"parts": [{"text": "Use the top nav to find Practice Tests."}]}}]}
        )

    monkeypatch.setattr(llm.httpx, "post", fake_post)

    reply = llm.send_chat(
        [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How do I take a practice test?"},
        ],
        "You are the EduSphere guide.",
    )

    assert reply == "Use the top nav to find Practice Tests."
    assert captured["url"] == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    assert captured["params"] == {"key": "fake-gemini-key"}
    assert captured["json"]["systemInstruction"] == {"parts": [{"text": "You are the EduSphere guide."}]}
    # "assistant" role is translated to Gemini's "model" role.
    assert captured["json"]["contents"] == [
        {"role": "user", "parts": [{"text": "hi"}]},
        {"role": "model", "parts": [{"text": "Hello!"}]},
        {"role": "user", "parts": [{"text": "How do I take a practice test?"}]},
    ]


def test_send_chat_anthropic_builds_request_and_parses_reply(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "fake-anthropic-key")
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(settings, "LLM_MODEL", "claude-sonnet-5")

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse({"content": [{"type": "text", "text": "Head to Practice Tests."}]})

    monkeypatch.setattr(llm.httpx, "post", fake_post)

    reply = llm.send_chat([{"role": "user", "content": "How do I take a practice test?"}], "system prompt")

    assert reply == "Head to Practice Tests."
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["x-api-key"] == "fake-anthropic-key"
    assert captured["json"]["system"] == "system prompt"
    assert captured["json"]["messages"] == [{"role": "user", "content": "How do I take a practice test?"}]
