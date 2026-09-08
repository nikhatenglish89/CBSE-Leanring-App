import secrets
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.core.email import send_email
from app.core.exceptions import AppError
from app.core.security import hash_password
from app.modules.auth import repository as auth_repo
from app.modules.classes import repository as classes_repo
from app.modules.courses import repository as courses_repo
from app.modules.users import repository as users_repo
from app.modules.users.models import User
from app.modules.users.schemas import AdminCreateUserRequest, UserUpdateRequest

# Excludes visually-confusable characters (0/O, 1/l/I) so a temporary
# password read aloud or copied by hand doesn't trip people up.
_PASSWORD_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"


def update_me(db: Session, user: User, payload: UserUpdateRequest) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.date_of_birth is not None:
        user.date_of_birth = payload.date_of_birth
    db.commit()
    db.refresh(user)
    return user


def _generate_temporary_password() -> str:
    return "".join(secrets.choice(_PASSWORD_ALPHABET) for _ in range(12))


def admin_create_user(db: Session, current_user: User, payload: AdminCreateUserRequest) -> tuple[User, str]:
    """Creates a Student, Teacher, or (Super Admin only) Admin account with
    a random temporary password; the account is forced to change it on
    first login (enforced client-side by must_reset_password, and
    re-checked by change_password clearing the flag). Returns the
    plaintext password once — it is never retrievable again after this
    call."""
    if payload.role == "ADMIN" and current_user.role.name != "SUPER_ADMIN":
        raise AppError("PERMISSION_DENIED", "Only Super Admins can create Admin accounts.", 403)

    if users_repo.get_user_by_email(db, payload.email) is not None:
        raise AppError("EMAIL_ALREADY_REGISTERED", "An account with this email already exists.", 409)

    role = auth_repo.get_role_by_name(db, payload.role)
    if role is None:
        raise AppError("INVALID_ROLE", f"Role '{payload.role}' is not available.", 400)

    temporary_password = _generate_temporary_password()
    user = users_repo.create_user(
        db,
        email=payload.email,
        password_hash=hash_password(temporary_password),
        full_name=payload.full_name,
        phone=payload.phone,
        role_id=role.id,
        password_reset_required=True,
    )

    if payload.role == "STUDENT":
        users_repo.create_student_profile(db, user.id)
    elif payload.role == "TEACHER":
        users_repo.create_teacher_profile(db, user.id)

    return user, temporary_password


def get_user_detail(db: Session, user_id: uuid.UUID) -> dict:
    user = users_repo.get_user_by_id(db, user_id)
    if user is None:
        raise AppError("USER_NOT_FOUND", "User not found.", 404)

    detail: dict = {"user": user}
    if user.role.name == "STUDENT":
        profile = users_repo.get_student_profile_by_user_id(db, user.id)
        klass = (
            classes_repo.get_class_by_id(db, profile.current_class_id)
            if profile and profile.current_class_id
            else None
        )
        detail["current_class_id"] = profile.current_class_id if profile else None
        detail["current_class_name"] = klass.name if klass else None
        detail["student_verified"] = profile.verified if profile else None
        detail["linked_parent"] = None
        if profile and profile.parent_profile_id:
            parent_profile = users_repo.get_parent_profile_by_id(db, profile.parent_profile_id)
            parent_user = users_repo.get_user_by_id(db, parent_profile.user_id) if parent_profile else None
            if parent_user is not None:
                detail["linked_parent"] = parent_user
    elif user.role.name == "TEACHER":
        profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
        detail["bio"] = profile.bio if profile else None
        detail["teacher_verified"] = profile.verified if profile else None
        if profile is not None:
            _, count = courses_repo.list_courses(db, 0, 1, teacher_id=profile.id)
            detail["course_count"] = count

    return detail


def get_verification_status(db: Session, user: User) -> bool:
    """Admin-approval status for a user's own role. Always True for roles
    the approval gate doesn't apply to (staff, parent)."""
    if user.role.name == "TEACHER":
        profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
        return bool(profile and profile.verified)
    if user.role.name == "STUDENT":
        profile = users_repo.get_student_profile_by_user_id(db, user.id)
        return bool(profile and profile.verified)
    return True


def set_user_verified(db: Session, user_id: uuid.UUID, verified: bool) -> User:
    user = users_repo.get_user_by_id(db, user_id)
    if user is None:
        raise AppError("USER_NOT_FOUND", "User not found.", 404)

    if user.role.name == "TEACHER":
        profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
        if profile is None:
            raise AppError("PROFILE_NOT_FOUND", "No teacher profile found for this account.", 400)
        users_repo.set_teacher_verified(db, profile, verified)
    elif user.role.name == "STUDENT":
        profile = users_repo.get_student_profile_by_user_id(db, user.id)
        if profile is None:
            raise AppError("PROFILE_NOT_FOUND", "No student profile found for this account.", 400)
        users_repo.set_student_verified(db, profile, verified)
    else:
        raise AppError("INVALID_ROLE", "Only Student and Teacher accounts can be verified.", 400)

    return user


def link_parent_to_student(db: Session, student_id: uuid.UUID, parent_user_id: uuid.UUID) -> User:
    student_user = users_repo.get_user_by_id(db, student_id)
    if student_user is None or student_user.role.name != "STUDENT":
        raise AppError("STUDENT_NOT_FOUND", "Student account not found.", 404)

    parent_user = users_repo.get_user_by_id(db, parent_user_id)
    if parent_user is None or parent_user.role.name != "PARENT":
        raise AppError("PARENT_NOT_FOUND", "Parent account not found.", 404)

    student_profile = users_repo.get_student_profile_by_user_id(db, student_user.id)
    if student_profile is None:
        raise AppError("PROFILE_NOT_FOUND", "No student profile found for this account.", 400)
    parent_profile = users_repo.get_parent_profile_by_user_id(db, parent_user.id)
    if parent_profile is None:
        raise AppError("PROFILE_NOT_FOUND", "No parent profile found for this account.", 400)

    users_repo.set_student_parent(db, student_profile, parent_profile.id)
    return student_user


def unlink_parent_from_student(db: Session, student_id: uuid.UUID) -> User:
    student_user = users_repo.get_user_by_id(db, student_id)
    if student_user is None or student_user.role.name != "STUDENT":
        raise AppError("STUDENT_NOT_FOUND", "Student account not found.", 404)

    student_profile = users_repo.get_student_profile_by_user_id(db, student_user.id)
    if student_profile is None:
        raise AppError("PROFILE_NOT_FOUND", "No student profile found for this account.", 400)

    users_repo.set_student_parent(db, student_profile, None)
    return student_user


def _send_birthday_email(user: User) -> bool:
    """Same shape/contract as send_verification_email in the auth module —
    returns whether the email actually went out, and never raises, so one
    bad address can't stop the rest of the day's batch."""
    text_body = (
        f"Hi {user.full_name},\n\n"
        "Happy Birthday from all of us at EduSphere CBSE! We hope you have a fantastic day.\n\n"
        "Wishing you a year full of learning and achievement."
    )
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color: #1558e0;">🎉 Happy Birthday, {user.full_name}!</h2>
      <p>Everyone at EduSphere CBSE is wishing you a fantastic day.</p>
      <p>Here's to a year full of learning and achievement ahead.</p>
    </div>
    """
    try:
        send_email(user.email, "Happy Birthday from EduSphere CBSE! 🎂", html_body, text_body)
        return True
    except Exception as exc:  # noqa: BLE001 - one failed send must not stop the rest of the batch
        print(f"[email:send-failed] to={user.email} error={exc}")
        return False


def send_birthday_emails(db: Session, today: date | None = None) -> int:
    """Sends a birthday email to every active user whose date_of_birth is
    today and hasn't already received one today. Intended to be called
    once a day by an external scheduler (Render's free tier has no
    built-in cron) — see the internal module's router."""
    today = today or date.today()
    sent_count = 0
    for user in users_repo.list_users_with_birthday_today(db, today):
        if _send_birthday_email(user):
            users_repo.mark_birthday_email_sent(db, user, today)
            sent_count += 1
    return sent_count
