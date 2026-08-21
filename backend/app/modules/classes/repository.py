import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.classes.models import Class


def list_classes(db: Session, offset: int, limit: int) -> tuple[list[Class], int]:
    items = db.scalars(
        select(Class).order_by(Class.display_order, Class.name).offset(offset).limit(limit)
    ).all()
    total = db.scalar(select(func.count()).select_from(Class)) or 0
    return list(items), total


def get_class_by_id(db: Session, class_id: uuid.UUID) -> Class | None:
    return db.get(Class, class_id)


def get_class_by_name(db: Session, name: str) -> Class | None:
    return db.scalar(select(Class).where(Class.name == name))


def create_class(db: Session, *, name: str, display_order: int) -> Class:
    obj = Class(name=name, display_order=display_order)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_class(db: Session, obj: Class, *, name: str | None, display_order: int | None) -> Class:
    if name is not None:
        obj.name = name
    if display_order is not None:
        obj.display_order = display_order
    db.commit()
    db.refresh(obj)
    return obj


def delete_class(db: Session, obj: Class) -> None:
    db.delete(obj)
    db.commit()
