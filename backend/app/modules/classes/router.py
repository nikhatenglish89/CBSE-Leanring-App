import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.classes import service as classes_service
from app.modules.classes.schemas import ClassCreateRequest, ClassOut, ClassUpdateRequest
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/classes", tags=["classes"])


@router.get("")
def list_classes(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
) -> dict:
    items, total = classes_service.list_classes(db, pagination.offset, pagination.page_size)
    data = [ClassOut.model_validate(c).model_dump(mode="json") for c in items]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("class:manage"))])
def create_class(payload: ClassCreateRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    obj = classes_service.create_class(db, payload)
    return success(ClassOut.model_validate(obj).model_dump(mode="json"))


@router.get("/{class_id}")
def get_class(class_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    obj = classes_service.get_class(db, class_id)
    return success(ClassOut.model_validate(obj).model_dump(mode="json"))


@router.patch("/{class_id}", dependencies=[Depends(require_permission("class:manage"))])
def update_class(
    class_id: uuid.UUID, payload: ClassUpdateRequest, db: Annotated[Session, Depends(get_db)]
) -> dict:
    obj = classes_service.update_class(db, class_id, payload)
    return success(ClassOut.model_validate(obj).model_dump(mode="json"))


@router.delete(
    "/{class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("class:manage"))],
)
def delete_class(class_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> None:
    classes_service.delete_class(db, class_id)
