from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
)
from app.modules.users.schemas import UserOut
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    user = auth_service.register(db, payload)
    return success(UserOut.from_user(user).model_dump(mode="json"))


@router.post("/login")
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    _, tokens = auth_service.login(db, payload.email, payload.password)
    return success(tokens.model_dump())


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    tokens = auth_service.refresh(db, payload.refresh_token)
    return success(tokens.model_dump())


@router.post("/logout")
def logout(payload: LogoutRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    auth_service.logout(db, payload.refresh_token)
    return success({"logged_out": True})
