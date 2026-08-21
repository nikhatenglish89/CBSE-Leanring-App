import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.modules.lessons import service as lessons_service
from app.modules.lessons.schemas import (
    LessonCreateRequest,
    LessonOut,
    LessonUpdateRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1", tags=["lessons"])


@router.get("/sections/{section_id}/lessons")
def list_lessons(section_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    lessons = lessons_service.list_lessons(db, current_user, section_id)
    return success([LessonOut.model_validate(item).model_dump(mode="json") for item in lessons])


@router.post("/sections/{section_id}/lessons", status_code=status.HTTP_201_CREATED)
def create_lesson(
    section_id: uuid.UUID,
    payload: LessonCreateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    lesson = lessons_service.create_lesson(db, current_user, section_id, payload)
    return success(LessonOut.model_validate(lesson).model_dump(mode="json"))


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    lesson = lessons_service.get_lesson(db, current_user, lesson_id)
    return success(LessonOut.model_validate(lesson).model_dump(mode="json"))


@router.patch("/lessons/{lesson_id}")
def update_lesson(
    lesson_id: uuid.UUID,
    payload: LessonUpdateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    lesson = lessons_service.update_lesson(db, current_user, lesson_id, payload)
    return success(LessonOut.model_validate(lesson).model_dump(mode="json"))


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(lesson_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    lessons_service.delete_lesson(db, current_user, lesson_id)
