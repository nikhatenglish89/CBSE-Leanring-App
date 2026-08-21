import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

VideoProvider = Literal["YOUTUBE", "VIMEO", "URL"]


class LessonMaterialOut(BaseModel):
    """Metadata only — the file bytes are served by the separate
    /materials/{id}/download endpoint, not embedded in this payload."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    material_type: str
    file_name: str
    mime_type: str
    file_size: int
    created_at: datetime


class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    provider: VideoProvider
    provider_ref: str
    title: str


class VideoSetRequest(BaseModel):
    url: str = Field(min_length=1, max_length=1000)
    title: str = ""


class MaterialBrowseOut(BaseModel):
    """A material plus enough context (lesson/course) to show and link to
    it from a platform-wide "Study Materials" browse page."""

    id: uuid.UUID
    material_type: str
    file_name: str
    mime_type: str
    file_size: int
    created_at: datetime
    lesson_id: uuid.UUID
    lesson_title: str
    course_id: uuid.UUID
    course_title: str

    @classmethod
    def from_row(cls, material, lesson, course) -> "MaterialBrowseOut":
        return cls(
            id=material.id,
            material_type=material.material_type,
            file_name=material.file_name,
            mime_type=material.mime_type,
            file_size=material.file_size,
            created_at=material.created_at,
            lesson_id=lesson.id,
            lesson_title=lesson.title,
            course_id=course.id,
            course_title=course.title,
        )


class VideoBrowseOut(BaseModel):
    id: uuid.UUID
    provider: VideoProvider
    provider_ref: str
    title: str
    lesson_id: uuid.UUID
    lesson_title: str
    course_id: uuid.UUID
    course_title: str

    @classmethod
    def from_row(cls, video, lesson, course) -> "VideoBrowseOut":
        return cls(
            id=video.id,
            provider=video.provider,
            provider_ref=video.provider_ref,
            title=video.title,
            lesson_id=lesson.id,
            lesson_title=lesson.title,
            course_id=course.id,
            course_title=course.title,
        )
