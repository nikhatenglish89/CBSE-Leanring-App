import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.feedback.models import Feedback


def create_feedback(db: Session, *, user_id: uuid.UUID, category: str, message: str) -> Feedback:
    obj = Feedback(user_id=user_id, category=category, message=message)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_feedback_by_id(db: Session, feedback_id: uuid.UUID) -> Feedback | None:
    return db.get(Feedback, feedback_id)


def list_feedback_for_user(db: Session, user_id: uuid.UUID) -> list[Feedback]:
    stmt = select(Feedback).where(Feedback.user_id == user_id).order_by(Feedback.created_at.desc())
    return list(db.scalars(stmt))


def list_all_feedback(
    db: Session, offset: int, limit: int, *, status: str | None = None, category: str | None = None
) -> tuple[list[Feedback], int]:
    stmt = select(Feedback)
    if status is not None:
        stmt = stmt.where(Feedback.status == status)
    if category is not None:
        stmt = stmt.where(Feedback.category == category)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Feedback.created_at.desc()).offset(offset).limit(limit)).all()
    return list(items), total


def update_status(db: Session, obj: Feedback, status: str) -> Feedback:
    obj.status = status
    db.commit()
    db.refresh(obj)
    return obj
