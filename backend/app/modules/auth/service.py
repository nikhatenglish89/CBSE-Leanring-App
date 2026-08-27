import uuid

from sqlalchemy.orm import Session

from app.core.captcha import generate_captcha_code, render_captcha_svg
from app.core.config import settings
from app.core.email import send_email
from app.core.exceptions import AppError
from app.core.security import (
    TokenError,
    create_access_token,
    create_captcha_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.base import utcnow
from app.modules.auth import repository as auth_repo
from app.modules.auth.schemas import CaptchaOut, ChangePasswordRequest, RegisterRequest, TokenPair
from app.modules.users import repository as users_repo
from app.modules.users.models import User


def _issue_token_pair(db: Session, user: User) -> TokenPair:
    access_token = create_access_token(str(user.id))
    refresh_token, jti, expires_at = create_refresh_token(str(user.id))
    auth_repo.create_refresh_token_record(db, user.id, jti, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def send_verification_email(user: User) -> bool:
    """Returns whether the email actually went out (or was a no-op in local
    dev with no SMTP configured — see app/core/email.py). Callers that need
    to tell the user the truth (e.g. a "Resend" button) should check this
    instead of assuming success."""
    token = create_email_verification_token(str(user.id))
    verify_link = f"{settings.FRONTEND_URL.rstrip('/')}/verify-email?token={token}"
    text_body = (
        f"Hi {user.full_name},\n\n"
        "Welcome to EduSphere CBSE! Please verify your email address by opening this link:\n"
        f"{verify_link}\n\n"
        "This link expires in 24 hours. If you didn't create this account, you can ignore this email."
    )
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color: #1558e0;">Welcome to EduSphere CBSE</h2>
      <p>Hi {user.full_name},</p>
      <p>Please verify your email address to finish setting up your account.</p>
      <p style="margin: 24px 0;">
        <a href="{verify_link}"
           style="background: #1a6ff5; color: #fff; padding: 12px 24px; border-radius: 8px;
                  text-decoration: none; font-weight: 600;">
          Verify my email
        </a>
      </p>
      <p style="color: #64748b; font-size: 13px;">
        This link expires in 24 hours. If you didn't create this account, you can ignore this email.
      </p>
    </div>
    """
    try:
        send_email(user.email, "Verify your EduSphere CBSE email", html_body, text_body)
        return True
    except Exception as exc:  # noqa: BLE001 - reported to the caller, not raised, so registration never fails on email delivery
        print(f"[email:send-failed] to={user.email} error={exc}")
        return False


def generate_captcha() -> CaptchaOut:
    code = generate_captcha_code()
    return CaptchaOut(token=create_captcha_token(code), svg=render_captcha_svg(code))


def verify_captcha(token: str, answer: str) -> None:
    try:
        payload = decode_token(token, expected_type="captcha")
    except TokenError as exc:
        raise AppError("CAPTCHA_INVALID", "That CAPTCHA has expired — please try again.", 400) from exc

    if payload["sub"].strip().upper() != answer.strip().upper():
        raise AppError("CAPTCHA_INVALID", "That didn't match — please try again.", 400)


def register(db: Session, payload: RegisterRequest) -> User:
    verify_captcha(payload.captcha_token, payload.captcha_answer)

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

    # Sending happens as a background task (scheduled by the router) so a
    # slow/unreachable mail server can never delay the signup response.
    return user


def verify_email(db: Session, token: str) -> User:
    try:
        payload = decode_token(token, expected_type="email_verify")
    except TokenError as exc:
        raise AppError("INVALID_TOKEN", "This verification link is invalid or expired.", 400) from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError("INVALID_TOKEN", "This verification link is invalid or expired.", 400) from exc

    user = users_repo.get_user_by_id(db, user_id)
    if user is None:
        raise AppError("INVALID_TOKEN", "This verification link is invalid or expired.", 400)

    if user.email_verified_at is None:
        user = users_repo.mark_email_verified(db, user)
    return user


def resend_verification_email(db: Session, user: User) -> None:
    if user.email_verified_at is not None:
        raise AppError("ALREADY_VERIFIED", "This email is already verified.", 400)
    if not send_verification_email(user):
        raise AppError(
            "EMAIL_SEND_FAILED", "Could not send the verification email right now. Please try again shortly.", 502
        )


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


def change_password(db: Session, user: User, payload: ChangePasswordRequest) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise AppError("CURRENT_PASSWORD_INCORRECT", "Current password is incorrect.", 400)

    user.password_hash = hash_password(payload.new_password)
    user.password_reset_required = False
    db.commit()
    # Force every other logged-in session to re-authenticate with the new
    # password; the caller's own session keeps working off its still-valid
    # access token.
    auth_repo.revoke_all_refresh_tokens_for_user(db, user.id)


def send_password_reset_email(user: User) -> bool:
    """Same shape/contract as send_verification_email — returns whether the
    email actually went out, so callers can decide whether to surface that."""
    token = create_password_reset_token(str(user.id))
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
    text_body = (
        f"Hi {user.full_name},\n\n"
        "We received a request to reset your EduSphere CBSE password. Open this link to choose a new one:\n"
        f"{reset_link}\n\n"
        "This link expires in 1 hour. If you didn't request this, you can safely ignore this email — "
        "your password will not be changed."
    )
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color: #1558e0;">Reset your EduSphere CBSE password</h2>
      <p>Hi {user.full_name},</p>
      <p>We received a request to reset your password. Click below to choose a new one.</p>
      <p style="margin: 24px 0;">
        <a href="{reset_link}"
           style="background: #1a6ff5; color: #fff; padding: 12px 24px; border-radius: 8px;
                  text-decoration: none; font-weight: 600;">
          Reset my password
        </a>
      </p>
      <p style="color: #64748b; font-size: 13px;">
        This link expires in 1 hour. If you didn't request this, you can safely ignore this email —
        your password will not be changed.
      </p>
    </div>
    """
    try:
        send_email(user.email, "Reset your EduSphere CBSE password", html_body, text_body)
        return True
    except Exception as exc:  # noqa: BLE001 - reported to the caller, not raised
        print(f"[email:send-failed] to={user.email} error={exc}")
        return False


def find_user_for_password_reset(db: Session, email: str) -> User | None:
    """Looks up the account synchronously (DB work must happen before the
    response, unlike the email send itself — see the register()/router
    background-task pattern). Returns None for a missing or inactive
    account so the router can skip queuing an email, without the caller
    ever finding out which case it was — the API response is identical
    either way, so a stranger can't use this endpoint to discover which
    emails have accounts."""
    user = users_repo.get_user_by_email(db, email)
    if user is None or user.status != "ACTIVE":
        return None
    return user


def reset_password(db: Session, token: str, new_password: str) -> None:
    try:
        payload = decode_token(token, expected_type="password_reset")
    except TokenError as exc:
        raise AppError("INVALID_TOKEN", "This reset link is invalid or expired.", 400) from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError("INVALID_TOKEN", "This reset link is invalid or expired.", 400) from exc

    user = users_repo.get_user_by_id(db, user_id)
    if user is None or user.status != "ACTIVE":
        raise AppError("INVALID_TOKEN", "This reset link is invalid or expired.", 400)

    user.password_hash = hash_password(new_password)
    user.password_reset_required = False
    db.commit()
    # Same defensive move as change_password: kick out any session an
    # attacker with the old (now-changed) password might already hold.
    auth_repo.revoke_all_refresh_tokens_for_user(db, user.id)


def logout(db: Session, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except TokenError:
        return  # already invalid — logout is idempotent
    record = auth_repo.get_refresh_token_by_jti(db, payload["jti"])
    if record is not None and not record.revoked:
        auth_repo.revoke_refresh_token(db, record)
