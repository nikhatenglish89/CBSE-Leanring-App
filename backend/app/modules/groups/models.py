import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Group(UUIDPKMixin, TimestampMixin, Base):
    """A teacher-created study group of students, used to assign shared
    tasks to the whole group at once."""

    __tablename__ = "groups"

    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")


class GroupMember(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "student_id", name="uq_group_members_group_student"),)

    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)


class GroupTask(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "group_tasks"

    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


class GroupTaskSubmission(UUIDPKMixin, TimestampMixin, Base):
    """A student's submitted work for a task — at most one per student per
    task; resubmitting replaces the content/file rather than creating a new
    row. An optional file attachment is stored as bytes directly on the row
    (same deliberate stand-in as LessonMaterial — see materials/models.py —
    no S3 credentials configured and Render's free tier has no persistent
    disk; keep uploads small, see MAX_UPLOAD_BYTES in service.py)."""

    __tablename__ = "group_task_submissions"
    __table_args__ = (UniqueConstraint("task_id", "student_id", name="uq_task_submissions_task_student"),)

    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("group_tasks.id"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    file_name: Mapped[str | None] = mapped_column(String(255), default=None)
    file_mime_type: Mapped[str | None] = mapped_column(String(150), default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, default=None)
    file_data: Mapped[bytes | None] = mapped_column(LargeBinary, default=None)
