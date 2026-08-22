import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Question(UUIDPKMixin, TimestampMixin, Base):
    """A student/parent's question posted on a specific lesson."""

    __tablename__ = "questions"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)


class Answer(UUIDPKMixin, TimestampMixin, Base):
    """At most one answer per question — answering again replaces it (any
    teacher/staff can answer or refine an answer, not just the course
    owner, same open-collaboration model as study materials/videos)."""

    __tablename__ = "answers"

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), unique=True, index=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)


class LiveClass(UUIDPKMixin, TimestampMixin, Base):
    """A scheduled live session with an external meeting link (Zoom/Meet/etc.)
    — this platform doesn't host video itself, same tradeoff as Video lessons
    only ever storing a link rather than hosting playback."""

    __tablename__ = "live_classes"

    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"), index=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teacher_profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    meeting_url: Mapped[str] = mapped_column(String(1000))
