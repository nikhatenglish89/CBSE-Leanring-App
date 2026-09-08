import hmac

from fastapi import Header

from app.core.config import settings
from app.core.exceptions import AppError


def require_cron_secret(x_cron_secret: str | None = Header(default=None)) -> None:
    """Gate for endpoints an external scheduler calls directly (no logged-in
    user) — compares against CRON_SECRET with a constant-time check so the
    endpoint isn't a timing oracle for guessing it. An unset CRON_SECRET
    refuses every request rather than accepting an empty header."""
    if not settings.CRON_SECRET or not x_cron_secret or not hmac.compare_digest(x_cron_secret, settings.CRON_SECRET):
        raise AppError("UNAUTHENTICATED", "Not authenticated.", 401)
