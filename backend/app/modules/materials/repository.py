import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.courses.models import Course, CourseSection
from app.modules.lessons.models import Lesson
from app.modules.materials.models import LessonMaterial, Video


def list_materials(db: Session, lesson_id: uuid.UUID) -> list[LessonMaterial]:
    stmt = (
        select(LessonMaterial)
        .where(LessonMaterial.lesson_id == lesson_id)
        .order_by(LessonMaterial.created_at)
    )
    return list(db.scalars(stmt))


def get_material_by_id(db: Session, material_id: uuid.UUID) -> LessonMaterial | None:
    return db.get(LessonMaterial, material_id)


def create_material(db: Session, **fields) -> LessonMaterial:
    obj = LessonMaterial(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def replace_material_file(
    db: Session, obj: LessonMaterial, *, file_name: str, mime_type: str, file_size: int, data: bytes,
    material_type: str,
) -> LessonMaterial:
    obj.file_name = file_name
    obj.mime_type = mime_type
    obj.file_size = file_size
    obj.data = data
    obj.material_type = material_type
    db.commit()
    db.refresh(obj)
    return obj


def delete_material(db: Session, obj: LessonMaterial) -> None:
    db.delete(obj)
    db.commit()


def get_video_by_lesson_id(db: Session, lesson_id: uuid.UUID) -> Video | None:
    return db.scalar(select(Video).where(Video.lesson_id == lesson_id))


def create_video(db: Session, **fields) -> Video:
    obj = Video(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_video(db: Session, obj: Video, *, provider: str, provider_ref: str, title: str) -> Video:
    obj.provider = provider
    obj.provider_ref = provider_ref
    obj.title = title
    db.commit()
    db.refresh(obj)
    return obj


def delete_video(db: Session, obj: Video) -> None:
    db.delete(obj)
    db.commit()


def _browse_scope(
    stmt, *, include_drafts: bool, only_free: bool, class_id: uuid.UUID | None, subject_id: uuid.UUID | None
):
    stmt = stmt.where(Course.deleted_at.is_(None), Lesson.deleted_at.is_(None))
    if not include_drafts:
        stmt = stmt.where(Course.status == "PUBLISHED")
    if only_free:
        stmt = stmt.where(Course.access_type == "FREE")
    if class_id is not None:
        stmt = stmt.where(Course.class_id == class_id)
    if subject_id is not None:
        stmt = stmt.where(Course.subject_id == subject_id)
    return stmt


def browse_materials(
    db: Session, offset: int, limit: int, *, include_drafts: bool = False, only_free: bool = False,
    class_id: uuid.UUID | None = None, subject_id: uuid.UUID | None = None,
) -> tuple[list[tuple[LessonMaterial, Lesson, Course]], int]:
    stmt = (
        select(LessonMaterial, Lesson, Course)
        .join(Lesson, LessonMaterial.lesson_id == Lesson.id)
        .join(CourseSection, Lesson.course_section_id == CourseSection.id)
        .join(Course, CourseSection.course_id == Course.id)
    )
    stmt = _browse_scope(
        stmt, include_drafts=include_drafts, only_free=only_free, class_id=class_id, subject_id=subject_id
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(
        stmt.order_by(LessonMaterial.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [tuple(row) for row in rows], total


def browse_videos(
    db: Session, offset: int, limit: int, *, include_drafts: bool = False, only_free: bool = False,
    class_id: uuid.UUID | None = None, subject_id: uuid.UUID | None = None,
) -> tuple[list[tuple[Video, Lesson, Course]], int]:
    stmt = (
        select(Video, Lesson, Course)
        .join(Lesson, Video.lesson_id == Lesson.id)
        .join(CourseSection, Lesson.course_section_id == CourseSection.id)
        .join(Course, CourseSection.course_id == Course.id)
    )
    stmt = _browse_scope(
        stmt, include_drafts=include_drafts, only_free=only_free, class_id=class_id, subject_id=subject_id
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(
        stmt.order_by(Video.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [tuple(row) for row in rows], total
