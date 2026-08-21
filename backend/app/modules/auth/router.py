from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    VerifyEmailRequest,
)
from app.modules.users.schemas import UserOut
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest, db: Annotated[Session, Depends(get_db)], background_tasks: BackgroundTasks
) -> dict:
    user = auth_service.register(db, payload)
    # Backgrounded so a slow/unreachable mail server never delays the signup
    # response itself — see auth_service.send_verification_email.
    background_tasks.add_task(auth_service.send_verification_email, user)
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


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    auth_service.verify_email(db, payload.token)
    return success({"verified": True})


@router.post("/resend-verification")
def resend_verification(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    auth_service.resend_verification_email(db, current_user)
    return success({"sent": True})
