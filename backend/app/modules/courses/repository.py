import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.modules.courses.models import Course, CourseSection


def list_courses(
    db: Session,
    offset: int,
    limit: int,
    *,
    status: str | None = None,
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    teacher_id: uuid.UUID | None = None,
) -> tuple[list[Course], int]:
    stmt = select(Course).where(Course.deleted_at.is_(None))
    if status is not None:
        stmt = stmt.where(Course.status == status)
    if class_id is not None:
        stmt = stmt.where(Course.class_id == class_id)
    if subject_id is not None:
        stmt = stmt.where(Course.subject_id == subject_id)
    if teacher_id is not None:
        stmt = stmt.where(Course.teacher_id == teacher_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Course.created_at.desc()).offset(offset).limit(limit)).all()
    return list(items), total


def get_course_by_id(db: Session, course_id: uuid.UUID) -> Course | None:
    obj = db.get(Course, course_id)
    if obj is not None and obj.deleted_at is not None:
        return None
    return obj


def create_course(db: Session, **fields) -> Course:
    obj = Course(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_course(db: Session, obj: Course, **fields) -> Course:
    for key, value in fields.items():
        if value is not None:
            setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def soft_delete_course(db: Session, obj: Course) -> None:
    obj.deleted_at = utcnow()
    db.commit()


def list_sections(db: Session, course_id: uuid.UUID) -> list[CourseSection]:
    stmt = (
        select(CourseSection)
        .where(CourseSection.course_id == course_id)
        .order_by(CourseSection.display_order)
    )
    return list(db.scalars(stmt))


def get_section_by_id(db: Session, section_id: uuid.UUID) -> CourseSection | None:
    return db.get(CourseSection, section_id)


def create_section(db: Session, **fields) -> CourseSection:
    obj = CourseSection(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_section(db: Session, obj: CourseSection, **fields) -> CourseSection:
    for key, value in fields.items():
        if value is not None:
            setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_section(db: Session, obj: CourseSection) -> None:
    db.delete(obj)
    db.commit()
