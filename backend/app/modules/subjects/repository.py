import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.modules.subjects.models import Chapter, Subject


def list_subjects(
    db: Session, offset: int, limit: int, *, class_id: uuid.UUID | None = None
) -> tuple[list[Subject], int]:
    stmt = select(Subject)
    if class_id is not None:
        stmt = stmt.where(Subject.class_id == class_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Subject.display_order, Subject.name).offset(offset).limit(limit)).all()
    return list(items), total


def get_subject_by_id(db: Session, subject_id: uuid.UUID) -> Subject | None:
    return db.get(Subject, subject_id)


def get_subject_by_class_and_name(db: Session, class_id: uuid.UUID, name: str) -> Subject | None:
    return db.scalar(select(Subject).where(Subject.class_id == class_id, Subject.name == name))


def create_subject(db: Session, *, class_id: uuid.UUID, name: str, display_order: int) -> Subject:
    obj = Subject(class_id=class_id, name=name, display_order=display_order)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_subject(db: Session, obj: Subject, *, name: str | None, display_order: int | None) -> Subject:
    if name is not None:
        obj.name = name
    if display_order is not None:
        obj.display_order = display_order
    db.commit()
    db.refresh(obj)
    return obj


def delete_subject(db: Session, obj: Subject) -> None:
    db.delete(obj)
    db.commit()


def list_chapters(db: Session, subject_id: uuid.UUID) -> list[Chapter]:
    stmt = (
        select(Chapter)
        .where(Chapter.subject_id == subject_id, Chapter.deleted_at.is_(None))
        .order_by(Chapter.display_order, Chapter.title)
    )
    return list(db.scalars(stmt))


def get_chapter_by_id(db: Session, chapter_id: uuid.UUID) -> Chapter | None:
    obj = db.get(Chapter, chapter_id)
    if obj is not None and obj.deleted_at is not None:
        return None
    return obj


def create_chapter(db: Session, *, subject_id: uuid.UUID, title: str, display_order: int) -> Chapter:
    obj = Chapter(subject_id=subject_id, title=title, display_order=display_order)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_chapter(db: Session, obj: Chapter, *, title: str | None, display_order: int | None) -> Chapter:
    if title is not None:
        obj.title = title
    if display_order is not None:
        obj.display_order = display_order
    db.commit()
    db.refresh(obj)
    return obj


def delete_chapter(db: Session, obj: Chapter) -> None:
    obj.deleted_at = utcnow()
    db.commit()
