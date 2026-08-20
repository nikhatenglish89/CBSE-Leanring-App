import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.users.models import User


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    status: str
    role: str
    created_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserOut":
        # `role` is a relationship (Role), not a plain column, so it needs
        # its own mapping rather than relying on from_attributes to coerce it.
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            status=user.status,
            role=user.role.name,
            created_at=user.created_at,
        )


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
