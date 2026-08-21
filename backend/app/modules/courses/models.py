import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Course(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "courses"

    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"), index=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teacher_profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    # Plain strings rather than DB enums, matching User.status elsewhere in
    # this codebase — adding a new value stays a data change, not a migration.
    access_type: Mapped[str] = mapped_column(String(20), default="FREE")  # FREE | PAID
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT | PUBLISHED


class CourseSection(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "course_sections"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
