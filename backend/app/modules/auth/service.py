from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.base import utcnow
from app.modules.auth import repository as auth_repo
from app.modules.auth.schemas import RegisterRequest, TokenPair
from app.modules.users import repository as users_repo
from app.modules.users.models import User


def _issue_token_pair(db: Session, user: User) -> TokenPair:
    access_token = create_access_token(str(user.id))
    refresh_token, jti, expires_at = create_refresh_token(str(user.id))
    auth_repo.create_refresh_token_record(db, user.id, jti, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def register(db: Session, payload: RegisterRequest) -> User:
    if users_repo.get_user_by_email(db, payload.email) is not None:
        raise AppError("EMAIL_ALREADY_REGISTERED", "An account with this email already exists.", 409)

    role = auth_repo.get_role_by_name(db, payload.role)
    if role is None:
        raise AppError("INVALID_ROLE", f"Role '{payload.role}' is not available for self-registration.", 400)

    user = users_repo.create_user(
        db,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        role_id=role.id,
    )

    if payload.role == "STUDENT":
        users_repo.create_student_profile(db, user.id)
    elif payload.role == "PARENT":
        users_repo.create_parent_profile(db, user.id)
    elif payload.role == "TEACHER":
        users_repo.create_teacher_profile(db, user.id)

    return user


def login(db: Session, email: str, password: str) -> tuple[User, TokenPair]:
    user = users_repo.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise AppError("INVALID_CREDENTIALS", "Incorrect email or password.", 401)
    if user.status != "ACTIVE":
        raise AppError("ACCOUNT_INACTIVE", "This account is not active.", 403)

    return user, _issue_token_pair(db, user)


def refresh(db: Session, refresh_token: str) -> TokenPair:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise AppError("INVALID_TOKEN", "Refresh token is invalid or expired.", 401) from exc

    record = auth_repo.get_refresh_token_by_jti(db, payload["jti"])
    if record is None or record.revoked:
        raise AppError("INVALID_TOKEN", "Refresh token is invalid or expired.", 401)

    expires_at = record.expires_at.replace(tzinfo=None) if record.expires_at.tzinfo else record.expires_at
    if expires_at < utcnow():
        raise AppError("INVALID_TOKEN", "Refresh token is invalid or expired.", 401)

    user = users_repo.get_user_by_id(db, record.user_id)
    if user is None or user.status != "ACTIVE":
        raise AppError("INVALID_TOKEN", "Refresh token is invalid or expired.", 401)

    # Rotate: revoke the used refresh token, issue a fresh pair.
    auth_repo.revoke_refresh_token(db, record)
    return _issue_token_pair(db, user)


def logout(db: Session, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except TokenError:
        return  # already invalid — logout is idempotent
    record = auth_repo.get_refresh_token_by_jti(db, payload["jti"])
    if record is not None and not record.revoked:
        auth_repo.revoke_refresh_token(db, record)
