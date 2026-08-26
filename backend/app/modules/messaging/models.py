import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Conversation(UUIDPKMixin, TimestampMixin, Base):
    """A single, persistent 1:1 thread between one student and one teacher —
    at most one conversation per (student, teacher) pair; new messages just
    append to it rather than starting a fresh thread each time they talk.
    Messaging is deliberately student<->teacher only (see service.py)."""

    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("student_id", "teacher_id", name="uq_conversation_student_teacher"),)

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)


class Message(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    # Set when the *other* participant has viewed it — drives the unread
    # badge in the conversation list.
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
