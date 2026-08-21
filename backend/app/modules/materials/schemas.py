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
