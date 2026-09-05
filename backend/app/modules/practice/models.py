import uuid

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class PracticeSet(UUIDPKMixin, TimestampMixin, Base):
    """A 20-question practice test for one class+subject combination.
    Reference/curriculum content owned by the platform (like Class/Subject),
    not user-generated — seeded, not created through a teacher-facing API.
    """

    __tablename__ = "practice_sets"

    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"), index=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    display_order: Mapped[int] = mapped_column(Integer, default=0)


class PracticeQuestion(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "practice_questions"

    practice_set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_sets.id"), index=True)
    question_text: Mapped[str] = mapped_column(Text)
    # Always exactly 4 options; enforced at the seed/content layer rather
    # than the DB, same tradeoff as options being a JSON list rather than a
    # separate options table — there is no per-question authoring UI yet.
    options: Mapped[list[str]] = mapped_column(JSON)
    correct_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text, default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0)


class PracticeAttempt(UUIDPKMixin, TimestampMixin, Base):
    """A completed submission of a practice set by a student — persisted
    so there's real history to show (e.g. a parent's view of their
    child's progress), not just a point-in-time score."""

    __tablename__ = "practice_attempts"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    practice_set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_sets.id"), index=True)
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
