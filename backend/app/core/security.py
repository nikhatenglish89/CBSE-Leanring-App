import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> tuple[str, str, datetime]:
    jti = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)
    expires_at_utc = now_utc + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        "iat": int(now_utc.timestamp()),
        "exp": int(expires_at_utc.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    # Returned as a naive UTC datetime (see app.models.base.utcnow): SQLite
    # (used for local dev/tests) doesn't reliably round-trip tzinfo, so
    # comparisons downstream stay naive-UTC throughout.
    return token, jti, expires_at_utc.replace(tzinfo=None)


def create_access_token(user_id: str) -> str:
    token, _, _ = _create_token(
        user_id, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return token


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    return _create_token(user_id, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


class TokenError(Exception):
    pass


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc

    if payload.get("type") != expected_type:
        raise TokenError(f"expected a {expected_type} token")

    return payload
