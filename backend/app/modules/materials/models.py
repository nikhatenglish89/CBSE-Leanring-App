import uuid

from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin

MATERIAL_TYPES = ("PDF", "DOCUMENT", "PRESENTATION", "IMAGE", "TEXT", "OTHER")

# Per docs/ARCHITECTURE.md, object storage is meant to sit behind a
# `StorageProvider` interface with S3 as the default adapter — but no S3
# credentials are configured for this deployment, and Render's free web
# service has no persistent disk. Storing the file bytes directly on the
# row in Postgres (Neon, which *is* persistent) is a deliberate stand-in
# until real object storage is wired up; keep uploads small (see
# MAX_UPLOAD_BYTES in service.py) so this stays practical.


class LessonMaterial(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "lesson_materials"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), index=True)
    material_type: Mapped[str] = mapped_column(String(20))
    file_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(150))
    file_size: Mapped[int] = mapped_column(Integer)
    data: Mapped[bytes] = mapped_column(LargeBinary)


class Video(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "videos"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), unique=True, index=True)
    # YOUTUBE | VIMEO | URL — inferred from the submitted link, not chosen
    # by the teacher, so the frontend knows how to embed it.
    provider: Mapped[str] = mapped_column(String(20))
    provider_ref: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(255), default="")
