from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Class(UUIDPKMixin, TimestampMixin, Base):
    """A CBSE grade level (e.g. "Class VIII") — root of the curriculum taxonomy."""

    __tablename__ = "classes"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
