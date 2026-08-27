from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import (
    CaptchaOut,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.modules.users import service as users_service
from app.modules.users.schemas import UserOut
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/captcha")
def get_captcha() -> dict:
    return success(auth_service.generate_captcha().model_dump())


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest, db: Annotated[Session, Depends(get_db)], background_tasks: BackgroundTasks
) -> dict:
    user = auth_service.register(db, payload)
    # Backgrounded so a slow/unreachable mail server never delays the signup
    # response itself — see auth_service.send_verification_email.
    background_tasks.add_task(auth_service.send_verification_email, user)
    is_verified = users_service.get_verification_status(db, user)
    return success(UserOut.from_user(user, is_verified=is_verified).model_dump(mode="json"))


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


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    auth_service.change_password(db, current_user, payload)
    return success({"changed": True})


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest, db: Annotated[Session, Depends(get_db)], background_tasks: BackgroundTasks
) -> dict:
    auth_service.verify_captcha(payload.captcha_token, payload.captcha_answer)

    # Response is identical whether or not the email has an account —
    # deliberately doesn't reveal which, same reasoning as
    # find_user_for_password_reset's docstring.
    user = auth_service.find_user_for_password_reset(db, payload.email)
    if user is not None:
        background_tasks.add_task(auth_service.send_password_reset_email, user)
    return success({"sent": True})


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    auth_service.reset_password(db, payload.token, payload.new_password)
    return success({"reset": True})
