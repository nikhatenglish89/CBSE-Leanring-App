import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.messaging import repository as messaging_repo
from app.modules.messaging.models import Conversation, Message
from app.modules.users import repository as users_repo
from app.modules.users.models import User

STAFF_ROLES = {"ADMIN", "SUPER_ADMIN"}


def _resolve_student_teacher(current_user: User, other_user: User) -> tuple[uuid.UUID, uuid.UUID]:
    """Messaging is strictly cross-role — one student, one teacher, never
    two of the same role and never anyone else (Parent/Admin/etc.)."""
    roles = {current_user.role.name, other_user.role.name}
    if roles != {"STUDENT", "TEACHER"}:
        raise AppError(
            "INVALID_PARTICIPANTS", "Conversations are only between a student and a teacher.", 400
        )
    if current_user.role.name == "STUDENT":
        return current_user.id, other_user.id
    return other_user.id, current_user.id


def start_conversation(db: Session, current_user: User, other_user_id: uuid.UUID) -> Conversation:
    if current_user.role.name not in ("STUDENT", "TEACHER"):
        raise AppError("PERMISSION_DENIED", "Only students and teachers can start conversations.", 403)

    other_user = users_repo.get_user_by_id(db, other_user_id)
    if other_user is None:
        raise AppError("USER_NOT_FOUND", "User not found.", 404)

    student_id, teacher_id = _resolve_student_teacher(current_user, other_user)

    # A student may only reach a teacher an admin has already approved —
    # same trust boundary as course publishing (courses/service.py).
    teacher_user_id = teacher_id
    teacher_profile = users_repo.get_teacher_profile_by_user_id(db, teacher_user_id)
    if teacher_profile is None or not teacher_profile.verified:
        raise AppError(
            "TEACHER_NOT_VERIFIED", "This teacher's account hasn't been approved by an admin yet.", 403
        )

    existing = messaging_repo.get_conversation_between(db, student_id, teacher_id)
    if existing is not None:
        return existing
    return messaging_repo.create_conversation(db, student_id=student_id, teacher_id=teacher_id)


def _is_participant(user: User, conversation: Conversation) -> bool:
    return user.id in (conversation.student_id, conversation.teacher_id)


def get_conversation_for_view(db: Session, user: User, conversation_id: uuid.UUID) -> Conversation:
    conversation = messaging_repo.get_conversation_by_id(db, conversation_id)
    if conversation is None:
        raise AppError("CONVERSATION_NOT_FOUND", "Conversation not found.", 404)
    # Staff can look (safety/moderation — see the module docstring in
    # models.py) but cannot participate; enforced separately below.
    if not _is_participant(user, conversation) and user.role.name not in STAFF_ROLES:
        raise AppError("CONVERSATION_NOT_FOUND", "Conversation not found.", 404)
    return conversation


def _assert_participant(user: User, conversation: Conversation) -> None:
    if not _is_participant(user, conversation):
        raise AppError("PERMISSION_DENIED", "You are not part of this conversation.", 403)


def _conversation_row(db: Session, user: User, conversation: Conversation):
    other_id = conversation.teacher_id if conversation.student_id == user.id else conversation.student_id
    other_user = users_repo.get_user_by_id(db, other_id)
    last_message = messaging_repo.get_last_message(db, conversation.id)
    unread = messaging_repo.count_unread(db, conversation.id, user.id)
    return conversation, other_user, last_message, unread


def start_conversation_row(db: Session, current_user: User, other_user_id: uuid.UUID):
    conversation = start_conversation(db, current_user, other_user_id)
    return _conversation_row(db, current_user, conversation)


def list_my_conversations(db: Session, user: User):
    if user.role.name not in ("STUDENT", "TEACHER"):
        return []
    conversations = messaging_repo.list_conversations_for_user(db, user.id)
    rows = [_conversation_row(db, user, conv) for conv in conversations]
    rows.sort(key=lambda row: row[2].created_at if row[2] else row[0].created_at, reverse=True)
    return rows


def send_message(db: Session, user: User, conversation_id: uuid.UUID, body: str) -> Message:
    conversation = get_conversation_for_view(db, user, conversation_id)
    _assert_participant(user, conversation)
    return messaging_repo.create_message(db, conversation_id=conversation.id, sender_id=user.id, body=body)


def list_messages(db: Session, user: User, conversation_id: uuid.UUID, offset: int, limit: int):
    conversation = get_conversation_for_view(db, user, conversation_id)
    messages, total = messaging_repo.list_messages(db, conversation.id, offset, limit)
    if _is_participant(user, conversation):
        # Staff viewing for moderation doesn't mark anything read — only an
        # actual participant opening the thread does.
        messaging_repo.mark_messages_read(db, conversation.id, user.id)
    senders = {uid: users_repo.get_user_by_id(db, uid) for uid in {m.sender_id for m in messages}}
    return [(m, senders[m.sender_id]) for m in messages], total


def list_messageable_users(db: Session, user: User, search: str | None) -> list[User]:
    if user.role.name == "STUDENT":
        candidates, _ = users_repo.list_users(db, 0, 50, role="TEACHER", search=search)
        # Only admin-approved teachers are contactable — same trust
        # boundary enforced again in start_conversation.
        return [t for t in candidates if (p := users_repo.get_teacher_profile_by_user_id(db, t.id)) and p.verified]
    if user.role.name == "TEACHER":
        students, _ = users_repo.list_users(db, 0, 50, role="STUDENT", search=search)
        return students
    return []


def list_all_conversations_for_moderation(db: Session, offset: int, limit: int):
    conversations, total = messaging_repo.list_all_conversations(db, offset, limit)
    rows = []
    for conv in conversations:
        student = users_repo.get_user_by_id(db, conv.student_id)
        teacher = users_repo.get_user_by_id(db, conv.teacher_id)
        last_message = messaging_repo.get_last_message(db, conv.id)
        count = messaging_repo.count_messages(db, conv.id)
        rows.append((conv, student, teacher, last_message, count))
    return rows, total
