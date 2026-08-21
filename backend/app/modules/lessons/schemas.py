import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ContentType = Literal["TEXT", "VIDEO", "PDF"]


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_section_id: uuid.UUID
    chapter_id: uuid.UUID | None
    title: str
    description: str
    content: str
    content_type: str
    display_order: int
    created_at: datetime


class LessonCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    content: str = ""
    content_type: ContentType = "TEXT"
    chapter_id: uuid.UUID | None = None
    display_order: int = 0


class LessonUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    content: str | None = None
    content_type: ContentType | None = None
    display_order: int | None = None
