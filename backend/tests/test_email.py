import httpx
import pytest

from app.core.config import settings
from app.core.email import RESEND_API_URL, send_email


def test_send_email_posts_to_resend_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "RESEND_API_KEY", "test-resend-key")
    monkeypatch.setattr(settings, "RESEND_FROM_EMAIL", "EduSphere CBSE <test@example.com>")

    captured = {}

    def fake_post(url, *, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return httpx.Response(200, json={"id": "abc123"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    send_email("student@example.com", "Hello", "<p>hi</p>", "hi")

    assert captured["url"] == RESEND_API_URL
    assert captured["headers"]["Authorization"] == "Bearer test-resend-key"
    assert captured["json"] == {
        "from": "EduSphere CBSE <test@example.com>",
        "to": ["student@example.com"],
        "subject": "Hello",
        "html": "<p>hi</p>",
        "text": "hi",
    }


def test_send_email_raises_on_resend_error(monkeypatch):
    monkeypatch.setattr(settings, "RESEND_API_KEY", "test-resend-key")

    def fake_post(url, *, headers, json, timeout):
        request = httpx.Request("POST", url)
        return httpx.Response(422, json={"message": "invalid from address"}, request=request)

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError):
        send_email("student@example.com", "Hello", "<p>hi</p>", "hi")


def test_send_email_prints_instead_of_sending_when_not_configured(monkeypatch, capsys):
    monkeypatch.setattr(settings, "RESEND_API_KEY", "")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("should not call Resend when not configured")

    monkeypatch.setattr(httpx, "post", fail_if_called)

    send_email("student@example.com", "Hello", "<p>hi</p>", "hi there")

    out = capsys.readouterr().out
    assert "email:not-configured" in out
    assert "student@example.com" in out
