import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class PracticeAttemptOut(BaseModel):
    id: uuid.UUID
    practice_set_title: str
    subject_name: str
    class_name: str
    score: int
    total: int
    created_at: datetime


class ChildTaskOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    due_date: datetime | None
    group_name: str
    teacher_name: str
    created_at: datetime


class ChildProgressOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    class_name: str | None
    tests_taken: int
    average_score_pct: float | None
    last_activity_at: datetime | None
    recent_attempts: list[PracticeAttemptOut]
    assigned_tasks: list[ChildTaskOut]
