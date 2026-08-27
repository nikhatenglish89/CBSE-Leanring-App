from typing import Literal

from pydantic import BaseModel, EmailStr, Field

SelfRegisterRole = Literal["STUDENT", "PARENT", "TEACHER"]


class CaptchaOut(BaseModel):
    token: str
    svg: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = None
    role: SelfRegisterRole = "STUDENT"
    captcha_token: str
    captcha_answer: str = Field(min_length=1, max_length=16)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str
    captcha_answer: str = Field(min_length=1, max_length=16)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class VerifyEmailRequest(BaseModel):
    token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    captcha_token: str
    captcha_answer: str = Field(min_length=1, max_length=16)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
