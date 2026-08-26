import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BannerOut(BaseModel):
    """Metadata only — the image bytes are served by the separate
    /banners/{id}/image endpoint, not embedded in this payload."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    link_url: str
    display_order: int
    is_active: bool
    created_at: datetime


class BannerUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    link_url: str | None = Field(default=None, max_length=1000)
    display_order: int | None = None
    is_active: bool | None = None
