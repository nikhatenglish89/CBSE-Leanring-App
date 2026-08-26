import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FeedbackCategory = Literal["BUG", "SUGGESTION", "GENERAL"]
FeedbackStatus = Literal["NEW", "REVIEWED", "RESOLVED"]


class FeedbackCreateRequest(BaseModel):
    category: FeedbackCategory
    message: str = Field(min_length=1, max_length=4000)


class FeedbackUpdateStatusRequest(BaseModel):
    status: FeedbackStatus


class FeedbackOut(BaseModel):
    id: uuid.UUID
    category: str
    message: str
    status: str
    created_at: datetime

    @classmethod
    def from_row(cls, feedback) -> "FeedbackOut":
        return cls(
            id=feedback.id,
            category=feedback.category,
            message=feedback.message,
            status=feedback.status,
            created_at=feedback.created_at,
        )


class AdminFeedbackOut(FeedbackOut):
    user_name: str
    user_email: str
    user_role: str

    @classmethod
    def from_row(cls, feedback, user) -> "AdminFeedbackOut":
        return cls(
            id=feedback.id,
            category=feedback.category,
            message=feedback.message,
            status=feedback.status,
            created_at=feedback.created_at,
            user_name=user.full_name,
            user_email=user.email,
            user_role=user.role.name,
        )
