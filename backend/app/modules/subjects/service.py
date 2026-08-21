import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.classes import repository as classes_repo
from app.modules.subjects import repository as subjects_repo
from app.modules.subjects.models import Chapter, Subject
from app.modules.subjects.schemas import (
    ChapterCreateRequest,
    ChapterUpdateRequest,
    SubjectCreateRequest,
    SubjectUpdateRequest,
)


def list_subjects(db: Session, offset: int, limit: int, class_id: uuid.UUID | None) -> tuple[list[Subject], int]:
    return subjects_repo.list_subjects(db, offset, limit, class_id=class_id)


def get_subject(db: Session, subject_id: uuid.UUID) -> Subject:
    obj = subjects_repo.get_subject_by_id(db, subject_id)
    if obj is None:
        raise AppError("SUBJECT_NOT_FOUND", "Subject not found.", 404)
    return obj


def create_subject(db: Session, payload: SubjectCreateRequest) -> Subject:
    if classes_repo.get_class_by_id(db, payload.class_id) is None:
        raise AppError("CLASS_NOT_FOUND", "Class not found.", 404)
    if subjects_repo.get_subject_by_class_and_name(db, payload.class_id, payload.name) is not None:
        raise AppError("SUBJECT_ALREADY_EXISTS", "This class already has a subject with this name.", 409)
    return subjects_repo.create_subject(
        db, class_id=payload.class_id, name=payload.name, display_order=payload.display_order
    )


def update_subject(db: Session, subject_id: uuid.UUID, payload: SubjectUpdateRequest) -> Subject:
    obj = get_subject(db, subject_id)
    return subjects_repo.update_subject(db, obj, name=payload.name, display_order=payload.display_order)


def delete_subject(db: Session, subject_id: uuid.UUID) -> None:
    obj = get_subject(db, subject_id)
    subjects_repo.delete_subject(db, obj)


def list_chapters(db: Session, subject_id: uuid.UUID) -> list[Chapter]:
    get_subject(db, subject_id)  # 404s if the subject doesn't exist
    return subjects_repo.list_chapters(db, subject_id)


def get_chapter(db: Session, chapter_id: uuid.UUID) -> Chapter:
    obj = subjects_repo.get_chapter_by_id(db, chapter_id)
    if obj is None:
        raise AppError("CHAPTER_NOT_FOUND", "Chapter not found.", 404)
    return obj


def create_chapter(db: Session, subject_id: uuid.UUID, payload: ChapterCreateRequest) -> Chapter:
    get_subject(db, subject_id)
    return subjects_repo.create_chapter(
        db, subject_id=subject_id, title=payload.title, display_order=payload.display_order
    )


def update_chapter(db: Session, chapter_id: uuid.UUID, payload: ChapterUpdateRequest) -> Chapter:
    obj = get_chapter(db, chapter_id)
    return subjects_repo.update_chapter(db, obj, title=payload.title, display_order=payload.display_order)


def delete_chapter(db: Session, chapter_id: uuid.UUID) -> None:
    obj = get_chapter(db, chapter_id)
    subjects_repo.delete_chapter(db, obj)
