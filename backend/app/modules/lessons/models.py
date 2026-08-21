import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Lesson(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "lessons"

    course_section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("course_sections.id"), index=True)
    # Optional link back to the curriculum tree so lessons stay
    # discoverable by chapter even though they're organized by course
    # structure (see docs/DATABASE_DESIGN.md, "Course/Learning Content").
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chapters.id"), default=None)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    # The actual lesson body (e.g. full poem/passage text for a TEXT
    # lesson) — separate from `description`, which is a short blurb shown
    # in syllabus listings.
    content: Mapped[str] = mapped_column(Text, default="")
    content_type: Mapped[str] = mapped_column(String(20), default="TEXT")  # TEXT | VIDEO | PDF
    display_order: Mapped[int] = mapped_column(Integer, default=0)
