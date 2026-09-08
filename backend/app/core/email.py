import httpx

from app.core.config import settings

RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Sends a single email via Resend's HTTP API (see .env.example).

    Not raw SMTP — Render's free tier blocks outbound SMTP ports entirely,
    so a real mail server is unreachable from there regardless of
    credentials; a plain HTTPS call has no such restriction.

    If Resend isn't configured (local dev with no API key set), this
    prints the email instead of sending it, so registration and other
    flows that trigger email still work with zero external setup.
    """
    if not settings.RESEND_API_KEY:
        message = f"[email:not-configured] to={to} subject={subject!r}\n{text_body}"
        try:
            print(message)
        except UnicodeEncodeError:
            # Windows' default console codepage can't render every
            # character (e.g. emoji) — fall back to an ASCII-safe form
            # rather than let a print() failure look like the send itself
            # failed.
            print(message.encode("ascii", errors="backslashreplace").decode("ascii"))
        return

    response = httpx.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
        json={
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        },
        timeout=10,
    )
    response.raise_for_status()
