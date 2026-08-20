import uuid
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import TokenError, decode_token
from app.modules.auth import repository as auth_repo
from app.modules.users import repository as users_repo
from app.modules.users.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise AppError("UNAUTHENTICATED", "Not authenticated.", 401)

    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except TokenError as exc:
        raise AppError("UNAUTHENTICATED", "Not authenticated.", 401) from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError("UNAUTHENTICATED", "Not authenticated.", 401) from exc

    user = users_repo.get_user_by_id(db, user_id)
    if user is None or user.status != "ACTIVE":
        raise AppError("UNAUTHENTICATED", "Not authenticated.", 401)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(permission_code: str):
    def _check(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> User:
        granted = auth_repo.get_permission_codes_for_role(db, user.role_id)
        if permission_code not in granted:
            raise AppError("PERMISSION_DENIED", "You do not have permission to do this.", 403)
        return user

    return _check
