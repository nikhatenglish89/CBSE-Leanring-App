import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.courses import service as courses_service
from app.modules.courses.schemas import (
    CourseCreateRequest,
    CourseOut,
    CourseSectionCreateRequest,
    CourseSectionOut,
    CourseSectionUpdateRequest,
    CourseUpdateRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("")
def list_courses(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    mine: bool = Query(False),
) -> dict:
    items, total = courses_service.list_courses(
        db,
        current_user,
        pagination.offset,
        pagination.page_size,
        class_id=class_id,
        subject_id=subject_id,
        mine=mine,
    )
    data = [CourseOut.model_validate(c).model_dump(mode="json") for c in items]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.post("", status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreateRequest, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    course = courses_service.create_course(db, current_user, payload)
    return success(CourseOut.model_validate(course).model_dump(mode="json"))


@router.get("/{course_id}")
def get_course(course_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    course = courses_service.get_course_for_view(db, current_user, course_id)
    return success(CourseOut.model_validate(course).model_dump(mode="json"))


@router.patch("/{course_id}")
def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    course = courses_service.update_course(db, current_user, course_id, payload)
    return success(CourseOut.model_validate(course).model_dump(mode="json"))


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    courses_service.delete_course(db, current_user, course_id)


@router.get("/{course_id}/sections")
def list_sections(course_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    sections = courses_service.list_sections(db, current_user, course_id)
    return success([CourseSectionOut.model_validate(s).model_dump(mode="json") for s in sections])


@router.post("/{course_id}/sections", status_code=status.HTTP_201_CREATED)
def create_section(
    course_id: uuid.UUID,
    payload: CourseSectionCreateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    section = courses_service.create_section(db, current_user, course_id, payload)
    return success(CourseSectionOut.model_validate(section).model_dump(mode="json"))


@router.patch("/sections/{section_id}")
def update_section(
    section_id: uuid.UUID,
    payload: CourseSectionUpdateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    section = courses_service.update_section(db, current_user, section_id, payload)
    return success(CourseSectionOut.model_validate(section).model_dump(mode="json"))


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> None:
    courses_service.delete_section(db, current_user, section_id)
