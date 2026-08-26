import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.modules.messaging.models import Conversation, Message


def get_conversation_between(db: Session, student_id: uuid.UUID, teacher_id: uuid.UUID) -> Conversation | None:
    return db.scalar(
        select(Conversation).where(
            Conversation.student_id == student_id, Conversation.teacher_id == teacher_id
        )
    )


def create_conversation(db: Session, *, student_id: uuid.UUID, teacher_id: uuid.UUID) -> Conversation:
    obj = Conversation(student_id=student_id, teacher_id=teacher_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_conversation_by_id(db: Session, conversation_id: uuid.UUID) -> Conversation | None:
    return db.get(Conversation, conversation_id)


def list_conversations_for_user(db: Session, user_id: uuid.UUID) -> list[Conversation]:
    stmt = select(Conversation).where(
        or_(Conversation.student_id == user_id, Conversation.teacher_id == user_id)
    )
    return list(db.scalars(stmt))


def list_all_conversations(db: Session, offset: int, limit: int) -> tuple[list[Conversation], int]:
    stmt = select(Conversation).order_by(Conversation.updated_at.desc())
    total = db.scalar(select(func.count()).select_from(Conversation)) or 0
    items = db.scalars(stmt.offset(offset).limit(limit)).all()
    return list(items), total


def get_last_message(db: Session, conversation_id: uuid.UUID) -> Message | None:
    return db.scalar(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )


def count_messages(db: Session, conversation_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
    ) or 0


def count_unread(db: Session, conversation_id: uuid.UUID, reader_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.sender_id != reader_id,
            Message.read_at.is_(None),
        )
    ) or 0


def list_messages(
    db: Session, conversation_id: uuid.UUID, offset: int, limit: int
) -> tuple[list[Message], int]:
    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    total = db.scalar(
        select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
    ) or 0
    items = db.scalars(stmt.offset(offset).limit(limit)).all()
    return list(items), total


def create_message(db: Session, *, conversation_id: uuid.UUID, sender_id: uuid.UUID, body: str) -> Message:
    msg = Message(conversation_id=conversation_id, sender_id=sender_id, body=body)
    db.add(msg)
    conversation = db.get(Conversation, conversation_id)
    if conversation is not None:
        # Bumped manually (not just relying on TimestampMixin's own
        # onupdate) so the conversation list can sort by recency without a
        # join against messages on every listing.
        conversation.updated_at = utcnow()
    db.commit()
    db.refresh(msg)
    return msg


def mark_messages_read(db: Session, conversation_id: uuid.UUID, reader_id: uuid.UUID) -> None:
    stmt = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.sender_id != reader_id,
        Message.read_at.is_(None),
    )
    now = utcnow()
    for msg in db.scalars(stmt):
        msg.read_at = now
    db.commit()
