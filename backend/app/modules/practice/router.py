import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.modules.practice import service as practice_service
from app.modules.practice.schemas import (
    PracticeQuestionOut,
    PracticeSetDetailOut,
    PracticeSetSummaryOut,
    PracticeSubmitRequest,
    PracticeSubmitResult,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1", tags=["practice"])


@router.get("/practice-sets")
def list_practice_sets(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
) -> dict:
    rows = practice_service.list_practice_sets(db, class_id=class_id, subject_id=subject_id)
    data = [
        PracticeSetSummaryOut.from_row(practice_set, klass, subject, count).model_dump(mode="json")
        for practice_set, klass, subject, count in rows
    ]
    return success(data)


@router.get("/practice-sets/{practice_set_id}")
def get_practice_set(
    practice_set_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    practice_set, klass, subject, questions = practice_service.get_practice_set_detail(db, practice_set_id)
    data = PracticeSetDetailOut(
        id=practice_set.id,
        class_id=klass.id,
        class_name=klass.name,
        subject_id=subject.id,
        subject_name=subject.name,
        title=practice_set.title,
        questions=[PracticeQuestionOut.model_validate(q) for q in questions],
    ).model_dump(mode="json")
    return success(data)


@router.post("/practice-sets/{practice_set_id}/submit")
def submit_practice_set(
    practice_set_id: uuid.UUID,
    payload: PracticeSubmitRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    score, total, results = practice_service.submit_practice_set(db, practice_set_id, current_user.id, payload)
    data = PracticeSubmitResult(score=score, total=total, results=results).model_dump(mode="json")
    return success(data)
