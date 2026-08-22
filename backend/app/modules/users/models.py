import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin
from app.modules.auth.models import Role


class User(UUIDPKMixin, TimestampMixin, Base):
    """Single identity table shared by every role.

    Role-specific data lives in StudentProfile/ParentProfile/TeacherProfile
    rather than extra nullable columns here (see docs/DATABASE_DESIGN.md,
    "Identity & RBAC" cluster note).
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, default=None)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    # NOTE: single role per user for v1 (simpler than the ERD's many-to-many
    # notation) — matches master spec §22's mutually-exclusive role list.
    # Multi-role support can be layered on with a join table later without
    # breaking the require_permission() contract.
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    # Set on accounts an admin creates (with a system-generated temporary
    # password); cleared the moment the user successfully changes their
    # password. Self-registered accounts never have this set.
    password_reset_required: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped["Role"] = relationship(lazy="joined")


class StudentProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    # Not FK-constrained yet: `classes` table doesn't exist until Phase 3.
    current_class_id: Mapped[uuid.UUID | None] = mapped_column(default=None)
    parent_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("parent_profiles.id"), default=None
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, default=None)


class ParentProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "parent_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)


class TeacherProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "teacher_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    bio: Mapped[str | None] = mapped_column(Text, default=None)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
