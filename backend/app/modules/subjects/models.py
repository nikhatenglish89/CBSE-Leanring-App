import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Subject(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "subjects"

    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    display_order: Mapped[int] = mapped_column(Integer, default=0)


class Chapter(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Scoped directly to a Subject rather than the ERD's Subject -> Book ->
    Chapter chain (see docs/DATABASE_DESIGN.md) — the Books/Topics layers are
    deferred until multiple textbooks per subject is an actual requirement.
    """

    __tablename__ = "chapters"

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
