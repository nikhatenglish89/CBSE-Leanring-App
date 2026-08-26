import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin

FEEDBACK_CATEGORIES = ("BUG", "SUGGESTION", "GENERAL")
FEEDBACK_STATUSES = ("NEW", "REVIEWED", "RESOLVED")


class Feedback(UUIDPKMixin, TimestampMixin, Base):
    """Free-form feedback from any signed-in user — bug reports,
    suggestions, or general comments — triaged by Admin/staff via status."""

    __tablename__ = "feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="NEW", index=True)
