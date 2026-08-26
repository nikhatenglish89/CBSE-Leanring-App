import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.feedback import service as feedback_service
from app.modules.feedback.schemas import (
    AdminFeedbackOut,
    FeedbackCreateRequest,
    FeedbackOut,
    FeedbackUpdateStatusRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreateRequest, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    feedback = feedback_service.submit_feedback(db, current_user, payload)
    return success(FeedbackOut.from_row(feedback).model_dump(mode="json"))


@router.get("/mine")
def list_my_feedback(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    items = feedback_service.list_my_feedback(db, current_user)
    return success([FeedbackOut.from_row(item).model_dump(mode="json") for item in items])


@router.get("", dependencies=[Depends(require_permission("feedback:manage"))])
def list_all_feedback(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    status_filter: str | None = None,
    category: str | None = None,
) -> dict:
    rows, total = feedback_service.list_all_feedback(
        db, pagination.offset, pagination.page_size, status=status_filter, category=category
    )
    data = [AdminFeedbackOut.from_row(item, user).model_dump(mode="json") for item, user in rows]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.patch("/{feedback_id}", dependencies=[Depends(require_permission("feedback:manage"))])
def update_feedback_status(
    feedback_id: uuid.UUID, payload: FeedbackUpdateStatusRequest, db: Annotated[Session, Depends(get_db)]
) -> dict:
    feedback = feedback_service.update_feedback_status(db, feedback_id, payload.status)
    return success(FeedbackOut.from_row(feedback).model_dump(mode="json"))
