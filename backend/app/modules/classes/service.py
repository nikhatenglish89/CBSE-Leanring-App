import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.classes import repository as classes_repo
from app.modules.classes.models import Class
from app.modules.classes.schemas import ClassCreateRequest, ClassUpdateRequest


def list_classes(db: Session, offset: int, limit: int) -> tuple[list[Class], int]:
    return classes_repo.list_classes(db, offset, limit)


def get_class(db: Session, class_id: uuid.UUID) -> Class:
    obj = classes_repo.get_class_by_id(db, class_id)
    if obj is None:
        raise AppError("CLASS_NOT_FOUND", "Class not found.", 404)
    return obj


def create_class(db: Session, payload: ClassCreateRequest) -> Class:
    if classes_repo.get_class_by_name(db, payload.name) is not None:
        raise AppError("CLASS_ALREADY_EXISTS", "A class with this name already exists.", 409)
    return classes_repo.create_class(db, name=payload.name, display_order=payload.display_order)


def update_class(db: Session, class_id: uuid.UUID, payload: ClassUpdateRequest) -> Class:
    obj = get_class(db, class_id)
    return classes_repo.update_class(db, obj, name=payload.name, display_order=payload.display_order)


def delete_class(db: Session, class_id: uuid.UUID) -> None:
    obj = get_class(db, class_id)
    classes_repo.delete_class(db, obj)
