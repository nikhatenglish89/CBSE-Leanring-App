import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

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
