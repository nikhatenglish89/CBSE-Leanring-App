import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.users import repository as users_repo
from app.modules.users import service as users_service
from app.modules.users.models import User
from app.modules.users.schemas import (
    AdminCreatedUserOut,
    AdminCreateUserRequest,
    UserDetailOut,
    UserOut,
    UserUpdateRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me")
def get_me(current_user: CurrentUser) -> dict:
    return success(UserOut.from_user(current_user).model_dump(mode="json"))


@router.patch("/me")
def patch_me(
    payload: UserUpdateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    updated = users_service.update_me(db, current_user, payload)
    return success(UserOut.from_user(updated).model_dump(mode="json"))


@router.get("", dependencies=[Depends(require_permission("user:view"))])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    role: str | None = None,
    search: str | None = None,
) -> dict:
    items, total = users_repo.list_users(
        db, pagination.offset, pagination.page_size, role=role, search=search
    )
    data = [UserOut.from_user(u).model_dump(mode="json") for u in items]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminCreateUserRequest,
    current_user: Annotated[User, Depends(require_permission("user:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    user, temporary_password = users_service.admin_create_user(db, current_user, payload)
    data = AdminCreatedUserOut.from_user_and_password(user, temporary_password).model_dump(mode="json")
    return success(data)


@router.get("/{user_id}", dependencies=[Depends(require_permission("user:view"))])
def get_user(user_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> dict:
    detail = users_service.get_user_detail(db, user_id)
    data = UserDetailOut(
        **UserOut.from_user(detail["user"]).model_dump(),
        current_class_id=detail.get("current_class_id"),
        current_class_name=detail.get("current_class_name"),
        date_of_birth=detail.get("date_of_birth"),
        bio=detail.get("bio"),
        teacher_verified=detail.get("teacher_verified"),
        course_count=detail.get("course_count"),
    ).model_dump(mode="json")
    return success(data)
