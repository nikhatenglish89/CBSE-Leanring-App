from sqlalchemy.orm import Session

from app.modules.users.models import User
from app.modules.users.schemas import UserUpdateRequest


def update_me(db: Session, user: User, payload: UserUpdateRequest) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    db.commit()
    db.refresh(user)
    return user
