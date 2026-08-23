import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.users.models import User

AdminCreatableRole = Literal["STUDENT", "TEACHER", "ADMIN"]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    status: str
    role: str
    email_verified: bool
    must_reset_password: bool
    # Admin-approval status (Student/Teacher only — always True for other
    # roles, since the approval gate doesn't apply to them). Gates whether
    # a teacher can publish a course and whether a student sees PAID
    # published content, not whether the account can log in.
    is_verified: bool
    created_at: datetime

    @classmethod
    def from_user(cls, user: User, *, is_verified: bool) -> "UserOut":
        # `role` is a relationship (Role), not a plain column, so it needs
        # its own mapping rather than relying on from_attributes to coerce it.
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            status=user.status,
            role=user.role.name,
            email_verified=user.email_verified_at is not None,
            must_reset_password=user.password_reset_required,
            is_verified=is_verified,
            created_at=user.created_at,
        )


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = None
    role: AdminCreatableRole


class AdminCreatedUserOut(UserOut):
    """Returned once, right after creation — the only time the plaintext
    temporary password is ever available."""

    temporary_password: str

    @classmethod
    def from_user_and_password(cls, user: User, temporary_password: str) -> "AdminCreatedUserOut":
        # A brand-new account is never pre-verified — Student/Teacher
        # accounts always start out needing admin approval.
        base = UserOut.from_user(user, is_verified=False)
        return cls(**base.model_dump(), temporary_password=temporary_password)


class UserDetailOut(UserOut):
    """UserOut plus role-specific profile fields an admin can review."""

    current_class_id: uuid.UUID | None = None
    current_class_name: str | None = None
    date_of_birth: date | None = None
    bio: str | None = None
    teacher_verified: bool | None = None
    student_verified: bool | None = None
    course_count: int | None = None
