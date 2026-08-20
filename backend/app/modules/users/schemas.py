import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    status: str
    created_at: datetime


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
