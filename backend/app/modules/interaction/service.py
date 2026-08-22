import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.classes import repository as classes_repo
from app.modules.courses.service import STAFF_ROLES
from app.modules.interaction import repository as interaction_repo
from app.modules.interaction.models import LiveClass, Question
from app.modules.interaction.schemas import (
    LiveClassCreateRequest,
    LiveClassUpdateRequest,
    QuestionCreateRequest,
)
from app.modules.lessons import service as lessons_service
from app.modules.subjects import repository as subjects_repo
from app.modules.users import repository as users_repo
from app.modules.users.models import User

_LEARNER_ROLES = {"STUDENT", "PARENT"}
_ANSWERING_ROLES = STAFF_ROLES | {"TEACHER"}


# --- Questions & answers -----------------------------------------------


def ask_question(db: Session, user: User, lesson_id: uuid.UUID, payload: QuestionCreateRequest) -> Question:
    if user.role.name not in _LEARNER_ROLES:
        raise AppError("PERMISSION_DENIED", "Only students and parents can ask questions.", 403)
    # Reuses the lesson's own visibility rule — 404s (not 403) on a lesson
    # the asker can't see, same as everywhere else lessons are gated.
    lessons_service.get_lesson(db, user, lesson_id)
    return interaction_repo.create_question(db, lesson_id=lesson_id, student_id=user.id, body=payload.body)


def list_questions_for_lesson(db: Session, user: User, lesson_id: uuid.UUID):
    lessons_service.get_lesson(db, user, lesson_id)
    return interaction_repo.list_questions_for_lesson(db, lesson_id)


def answer_question(db: Session, user: User, question_id: uuid.UUID, body: str):
    if user.role.name not in _ANSWERING_ROLES:
        raise AppError("PERMISSION_DENIED", "Only teachers can answer questions.", 403)
    question = interaction_repo.get_question_by_id(db, question_id)
    if question is None:
        raise AppError("QUESTION_NOT_FOUND", "Question not found.", 404)
    # Make sure the answering teacher can actually see the underlying lesson
    # (e.g. not a draft course belonging to nobody they'd have access to).
    lessons_service.get_lesson(db, user, question.lesson_id)
    return interaction_repo.upsert_answer(db, question_id=question.id, teacher_id=user.id, body=body)


def browse_questions(
    db: Session,
    user: User,
    offset: int,
    limit: int,
    *,
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    answered: bool | None = None,
    mine: bool = False,
):
    include_drafts = user.role.name not in _LEARNER_ROLES
    student_id = user.id if mine else None
    return interaction_repo.browse_questions(
        db,
        offset,
        limit,
        include_drafts=include_drafts,
        class_id=class_id,
        subject_id=subject_id,
        answered=answered,
        student_id=student_id,
    )


# --- Live classes ---------------------------------------------------------


def _is_staff(user: User) -> bool:
    return user.role.name in STAFF_ROLES


def _resolve_teacher_profile_id(db: Session, user: User) -> uuid.UUID:
    if user.role.name != "TEACHER":
        raise AppError("PERMISSION_DENIED", "Only teachers can schedule live classes.", 403)
    profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
    if profile is None:
        raise AppError("TEACHER_PROFILE_MISSING", "No teacher profile found for this account.", 400)
    return profile.id


def create_live_class(db: Session, user: User, payload: LiveClassCreateRequest) -> LiveClass:
    if classes_repo.get_class_by_id(db, payload.class_id) is None:
        raise AppError("CLASS_NOT_FOUND", "Class not found.", 404)
    if subjects_repo.get_subject_by_id(db, payload.subject_id) is None:
        raise AppError("SUBJECT_NOT_FOUND", "Subject not found.", 404)
    teacher_id = _resolve_teacher_profile_id(db, user)
    return interaction_repo.create_live_class(
        db,
        class_id=payload.class_id,
        subject_id=payload.subject_id,
        teacher_id=teacher_id,
        title=payload.title,
        description=payload.description,
        scheduled_at=payload.scheduled_at,
        meeting_url=payload.meeting_url,
    )


def _assert_can_manage_live_class(db: Session, user: User, live_class: LiveClass) -> None:
    if _is_staff(user):
        return
    profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
    if profile is None or live_class.teacher_id != profile.id:
        raise AppError("PERMISSION_DENIED", "You do not have permission to do this.", 403)


def update_live_class(
    db: Session, user: User, live_class_id: uuid.UUID, payload: LiveClassUpdateRequest
) -> LiveClass:
    live_class = interaction_repo.get_live_class_by_id(db, live_class_id)
    if live_class is None:
        raise AppError("LIVE_CLASS_NOT_FOUND", "Live class not found.", 404)
    _assert_can_manage_live_class(db, user, live_class)
    return interaction_repo.update_live_class(
        db,
        live_class,
        title=payload.title,
        description=payload.description,
        scheduled_at=payload.scheduled_at,
        meeting_url=payload.meeting_url,
    )


def delete_live_class(db: Session, user: User, live_class_id: uuid.UUID) -> None:
    live_class = interaction_repo.get_live_class_by_id(db, live_class_id)
    if live_class is None:
        raise AppError("LIVE_CLASS_NOT_FOUND", "Live class not found.", 404)
    _assert_can_manage_live_class(db, user, live_class)
    interaction_repo.delete_live_class(db, live_class)


def browse_live_classes(
    db: Session,
    offset: int,
    limit: int,
    *,
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    upcoming_only: bool = False,
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return interaction_repo.browse_live_classes(
        db, offset, limit, class_id=class_id, subject_id=subject_id, upcoming_only=upcoming_only, now=now
    )
