import uuid

from pydantic import BaseModel, ConfigDict, Field


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    class_id: uuid.UUID
    name: str
    display_order: int


class SubjectCreateRequest(BaseModel):
    class_id: uuid.UUID
    name: str = Field(min_length=1, max_length=100)
    display_order: int = 0


class SubjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    display_order: int | None = None


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    display_order: int


class ChapterCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    display_order: int = 0


class ChapterUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    display_order: int | None = None
