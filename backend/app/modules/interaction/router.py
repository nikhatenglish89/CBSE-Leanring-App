import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.interaction import repository as interaction_repo
from app.modules.interaction import service as interaction_service
from app.modules.interaction.schemas import (
    AnswerOut,
    AnswerUpsertRequest,
    LiveClassCreateRequest,
    LiveClassOut,
    LiveClassUpdateRequest,
    QuestionBrowseOut,
    QuestionCreateRequest,
    QuestionOut,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1", tags=["interaction"])


@router.post("/lessons/{lesson_id}/questions", status_code=status.HTTP_201_CREATED)
def ask_question(
    lesson_id: uuid.UUID,
    payload: QuestionCreateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    question = interaction_service.ask_question(db, current_user, lesson_id, payload)
    data = QuestionOut.from_row(question, current_user, None, None).model_dump(mode="json")
    return success(data)


@router.get("/lessons/{lesson_id}/questions")
def list_questions_for_lesson(
    lesson_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    rows = interaction_service.list_questions_for_lesson(db, current_user, lesson_id)
    data = [
        QuestionOut.from_row(question, student, answer, answerer).model_dump(mode="json")
        for question, student, answer, answerer in rows
    ]
    return success(data)


@router.post("/questions/{question_id}/answer")
def answer_question(
    question_id: uuid.UUID,
    payload: AnswerUpsertRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    answer = interaction_service.answer_question(db, current_user, question_id, payload.body)
    data = AnswerOut.from_row(answer, current_user).model_dump(mode="json")
    return success(data)


@router.get("/questions")
def browse_questions(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    answered: bool | None = None,
    mine: bool = False,
) -> dict:
    rows, total = interaction_service.browse_questions(
        db,
        current_user,
        pagination.offset,
        pagination.page_size,
        class_id=class_id,
        subject_id=subject_id,
        answered=answered,
        mine=mine,
    )
    data = [
        QuestionBrowseOut.from_row(
            question, student, answer, answerer, lesson, course, klass, subject
        ).model_dump(mode="json")
        for question, student, answer, answerer, lesson, course, klass, subject in rows
    ]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


def _live_class_out(db: Session, live_class) -> dict:
    context = interaction_repo.get_live_class_context(db, live_class)
    if context is None:
        raise AppError("LIVE_CLASS_NOT_FOUND", "Live class not found.", 404)
    klass, subject, teacher = context
    return LiveClassOut.from_row(live_class, klass, subject, teacher).model_dump(mode="json")


@router.post("/live-classes", status_code=status.HTTP_201_CREATED)
def create_live_class(
    payload: LiveClassCreateRequest, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    live_class = interaction_service.create_live_class(db, current_user, payload)
    return success(_live_class_out(db, live_class))


@router.get("/live-classes")
def browse_live_classes(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    upcoming_only: bool = False,
) -> dict:
    rows, total = interaction_service.browse_live_classes(
        db,
        pagination.offset,
        pagination.page_size,
        class_id=class_id,
        subject_id=subject_id,
        upcoming_only=upcoming_only,
    )
    data = [
        LiveClassOut.from_row(live_class, klass, subject, teacher).model_dump(mode="json")
        for live_class, klass, subject, teacher in rows
    ]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.patch("/live-classes/{live_class_id}")
def update_live_class(
    live_class_id: uuid.UUID,
    payload: LiveClassUpdateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    live_class = interaction_service.update_live_class(db, current_user, live_class_id, payload)
    return success(_live_class_out(db, live_class))


@router.delete("/live-classes/{live_class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_live_class(
    live_class_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> None:
    interaction_service.delete_live_class(db, current_user, live_class_id)
