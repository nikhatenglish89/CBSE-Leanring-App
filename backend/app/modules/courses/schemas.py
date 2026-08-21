import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AccessType = Literal["FREE", "PAID"]
CourseStatus = Literal["DRAFT", "PUBLISHED"]


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    class_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    title: str
    description: str
    access_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class CourseCreateRequest(BaseModel):
    class_id: uuid.UUID
    subject_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    access_type: AccessType = "FREE"
    # Only honored for ADMIN/SUPER_ADMIN/CONTENT_MANAGER callers — a TEACHER
    # always becomes the owner of a course they create, via their own
    # teacher profile, regardless of what (if anything) they send here.
    teacher_id: uuid.UUID | None = None


class CourseUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    access_type: AccessType | None = None
    status: CourseStatus | None = None


class CourseSectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    display_order: int


class CourseSectionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    display_order: int = 0


class CourseSectionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    display_order: int | None = None
