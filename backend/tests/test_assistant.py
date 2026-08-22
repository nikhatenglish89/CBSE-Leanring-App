from app.core import llm
from tests.test_curriculum import _auth_headers


def test_chat_requires_auth(client):
    resp = client.post("/api/v1/assistant/chat", json={"message": "How do I take a practice test?"})
    assert resp.status_code == 401


def test_chat_without_api_key_returns_configured_false(client):
    # Test settings never set LLM_API_KEY, so this always hits the fallback path.
    headers = _auth_headers(client, "assistant.nokey@example.com", "STUDENT")
    resp = client.post(
        "/api/v1/assistant/chat", json={"message": "How do I take a practice test?"}, headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["configured"] is False
    assert "not fully set up" in body["reply"]


def test_chat_rejects_empty_message(client):
    headers = _auth_headers(client, "assistant.empty@example.com", "STUDENT")
    resp = client.post("/api/v1/assistant/chat", json={"message": ""}, headers=headers)
    assert resp.status_code == 422


def test_chat_rejects_oversized_history(client):
    headers = _auth_headers(client, "assistant.bighist@example.com", "STUDENT")
    history = [{"role": "user", "content": "hi"} for _ in range(21)]
    resp = client.post(
        "/api/v1/assistant/chat", json={"message": "hi", "history": history}, headers=headers
    )
    assert resp.status_code == 422


def test_chat_uses_llm_when_configured(client, monkeypatch):
    headers = _auth_headers(client, "assistant.configured@example.com", "STUDENT")

    monkeypatch.setattr(llm, "is_configured", lambda: True)

    captured = {}

    def fake_send_chat(messages, system_prompt):
        captured["messages"] = messages
        captured["system_prompt"] = system_prompt
        return "Head to Practice Tests in the top nav and pick a class/subject."

    monkeypatch.setattr(llm, "send_chat", fake_send_chat)

    resp = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "How do I take a practice test?",
            "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "Hello!"}],
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["configured"] is True
    assert "Practice Tests" in body["reply"]
    assert captured["messages"][-1] == {"role": "user", "content": "How do I take a practice test?"}
    assert len(captured["messages"]) == 3
    assert "EduSphere CBSE" in captured["system_prompt"]
    assert "STUDENT" in captured["system_prompt"]


def test_chat_handles_llm_failure_gracefully(client, monkeypatch):
    headers = _auth_headers(client, "assistant.failure@example.com", "STUDENT")

    monkeypatch.setattr(llm, "is_configured", lambda: True)

    def failing_send_chat(messages, system_prompt):
        raise ValueError("boom")

    monkeypatch.setattr(llm, "send_chat", failing_send_chat)

    resp = client.post(
        "/api/v1/assistant/chat", json={"message": "How do I take a practice test?"}, headers=headers
    )
    assert resp.status_code == 502
    assert resp.json()["error"]["code"] == "ASSISTANT_UNAVAILABLE"
