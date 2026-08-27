import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
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
