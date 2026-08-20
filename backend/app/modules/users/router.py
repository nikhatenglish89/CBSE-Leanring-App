from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.users import repository as users_repo
from app.modules.users import service as users_service
from app.modules.users.schemas import UserOut, UserUpdateRequest
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
) -> dict:
    items, total = users_repo.list_users(db, pagination.offset, pagination.page_size)
    data = [UserOut.from_user(u).model_dump(mode="json") for u in items]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})
