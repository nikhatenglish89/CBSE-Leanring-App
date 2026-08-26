import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.feedback import repository as feedback_repo
from app.modules.feedback.models import Feedback
from app.modules.feedback.schemas import FeedbackCreateRequest
from app.modules.users import repository as users_repo
from app.modules.users.models import User


def submit_feedback(db: Session, user: User, payload: FeedbackCreateRequest) -> Feedback:
    return feedback_repo.create_feedback(
        db, user_id=user.id, category=payload.category, message=payload.message
    )


def list_my_feedback(db: Session, user: User) -> list[Feedback]:
    return feedback_repo.list_feedback_for_user(db, user.id)


def list_all_feedback(
    db: Session, offset: int, limit: int, *, status: str | None, category: str | None
) -> tuple[list[tuple[Feedback, User]], int]:
    items, total = feedback_repo.list_all_feedback(db, offset, limit, status=status, category=category)
    rows = [(item, users_repo.get_user_by_id(db, item.user_id)) for item in items]
    return rows, total


def update_feedback_status(db: Session, feedback_id: uuid.UUID, status: str) -> Feedback:
    feedback = feedback_repo.get_feedback_by_id(db, feedback_id)
    if feedback is None:
        raise AppError("FEEDBACK_NOT_FOUND", "Feedback not found.", 404)
    return feedback_repo.update_status(db, feedback, status)
