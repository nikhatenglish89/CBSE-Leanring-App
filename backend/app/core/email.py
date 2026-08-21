import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_email(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Sends a single email via SMTP (Gmail by default — see .env.example).

    If SMTP isn't configured (local dev with no credentials set), this
    prints the email instead of sending it, so registration and other
    flows that trigger email still work with zero external setup.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[email:not-configured] to={to} subject={subject!r}\n{text_body}")
        return

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)
