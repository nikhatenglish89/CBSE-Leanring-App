import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.subjects import service as subjects_service
from app.modules.subjects.schemas import (
    ChapterCreateRequest,
    ChapterOut,
    ChapterUpdateRequest,
    SubjectCreateRequest,
    SubjectOut,
    SubjectUpdateRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/subjects", tags=["subjects"])
chapter_router = APIRouter(prefix="/api/v1/chapters", tags=["subjects"])


@router.get("")
def list_subjects(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    class_id: uuid.UUID | None = None,
) -> dict:
    items, total = subjects_service.list_subjects(db, pagination.offset, pagination.page_size, class_id)
    data = [SubjectOut.model_validate(s).model_dump(mode="json") for s in items]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("subject:manage"))])
def create_subject(payload: SubjectCreateRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    obj = subjects_service.create_subject(db, payload)
    return success(SubjectOut.model_validate(obj).model_dump(mode="json"))


@router.get("/{subject_id}")
def get_subject(subject_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    obj = subjects_service.get_subject(db, subject_id)
    return success(SubjectOut.model_validate(obj).model_dump(mode="json"))


@router.patch("/{subject_id}", dependencies=[Depends(require_permission("subject:manage"))])
def update_subject(
    subject_id: uuid.UUID, payload: SubjectUpdateRequest, db: Annotated[Session, Depends(get_db)]
) -> dict:
    obj = subjects_service.update_subject(db, subject_id, payload)
    return success(SubjectOut.model_validate(obj).model_dump(mode="json"))


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("subject:manage"))],
)
def delete_subject(subject_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> None:
    subjects_service.delete_subject(db, subject_id)


@router.get("/{subject_id}/chapters")
def list_chapters(subject_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    chapters = subjects_service.list_chapters(db, subject_id)
    return success([ChapterOut.model_validate(c).model_dump(mode="json") for c in chapters])


@router.post(
    "/{subject_id}/chapters",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("chapter:manage"))],
)
def create_chapter(
    subject_id: uuid.UUID, payload: ChapterCreateRequest, db: Annotated[Session, Depends(get_db)]
) -> dict:
    chapter = subjects_service.create_chapter(db, subject_id, payload)
    return success(ChapterOut.model_validate(chapter).model_dump(mode="json"))


@chapter_router.get("/{chapter_id}")
def get_chapter(chapter_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    obj = subjects_service.get_chapter(db, chapter_id)
    return success(ChapterOut.model_validate(obj).model_dump(mode="json"))


@chapter_router.patch("/{chapter_id}", dependencies=[Depends(require_permission("chapter:manage"))])
def update_chapter(
    chapter_id: uuid.UUID, payload: ChapterUpdateRequest, db: Annotated[Session, Depends(get_db)]
) -> dict:
    obj = subjects_service.update_chapter(db, chapter_id, payload)
    return success(ChapterOut.model_validate(obj).model_dump(mode="json"))


@chapter_router.delete(
    "/{chapter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("chapter:manage"))],
)
def delete_chapter(chapter_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> None:
    subjects_service.delete_chapter(db, chapter_id)
