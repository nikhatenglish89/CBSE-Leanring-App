import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request

from app.core.exceptions import AppError

# In-memory sliding-window counters. Resets on process restart and isn't
# shared across multiple instances — acceptable for this app's single-Render-
# instance deployment; would need a shared store (e.g. Redis) to hold up
# under horizontal scaling.
_buckets: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()

_TOO_MANY_ATTEMPTS = "Too many attempts — please wait a bit before trying again."


def _hit(key: str, max_requests: int, window_seconds: float) -> None:
    now = time.monotonic()
    with _lock:
        bucket = _buckets[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= max_requests:
            raise AppError("RATE_LIMITED", _TOO_MANY_ATTEMPTS, 429)
        bucket.append(now)


def _clear(key: str) -> None:
    with _lock:
        _buckets.pop(key, None)


def rate_limit_by_ip(key_prefix: str, max_requests: int, window_seconds: float):
    """FastAPI dependency: throttles by client IP, checked before the
    request body is even parsed — the first line of defense against a
    single source hammering an endpoint."""

    def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        _hit(f"{key_prefix}:ip:{client_ip}", max_requests, window_seconds)

    return _dependency


def check_login_attempts(email: str) -> None:
    """Throttles by the *target account* rather than the caller — closes
    the gap where one solved CAPTCHA could otherwise be replayed across
    many login attempts against the same account from anywhere."""
    _hit(f"login:email:{email.lower()}", max_requests=8, window_seconds=900)


def clear_login_attempts(email: str) -> None:
    _clear(f"login:email:{email.lower()}")


def check_forgot_password_attempts(email: str) -> None:
    """Throttles by the *target* email so an attacker can't repeatedly
    trigger reset emails at someone else's inbox."""
    _hit(f"forgot-password:email:{email.lower()}", max_requests=3, window_seconds=3600)
