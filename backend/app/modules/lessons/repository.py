import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.modules.lessons.models import Lesson


def list_lessons(db: Session, section_id: uuid.UUID) -> list[Lesson]:
    stmt = (
        select(Lesson)
        .where(Lesson.course_section_id == section_id, Lesson.deleted_at.is_(None))
        .order_by(Lesson.display_order)
    )
    return list(db.scalars(stmt))


def get_lesson_by_id(db: Session, lesson_id: uuid.UUID) -> Lesson | None:
    obj = db.get(Lesson, lesson_id)
    if obj is not None and obj.deleted_at is not None:
        return None
    return obj


def create_lesson(db: Session, **fields) -> Lesson:
    obj = Lesson(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_lesson(db: Session, obj: Lesson, **fields) -> Lesson:
    for key, value in fields.items():
        if value is not None:
            setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def soft_delete_lesson(db: Session, obj: Lesson) -> None:
    obj.deleted_at = utcnow()
    db.commit()
