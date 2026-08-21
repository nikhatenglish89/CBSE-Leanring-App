import uuid

from pydantic import BaseModel, ConfigDict, Field


class ClassOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    display_order: int


class ClassCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    display_order: int = 0


class ClassUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    display_order: int | None = None
