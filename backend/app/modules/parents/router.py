from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.dependencies.auth import CurrentUser
from app.modules.parents import service as parents_service
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/parents", tags=["parents"])


@router.get("/children")
def list_children(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    if current_user.role.name != "PARENT":
        raise AppError("PERMISSION_DENIED", "Only parent accounts can view this.", 403)
    children = parents_service.list_children_progress(db, current_user)
    return success([c.model_dump(mode="json") for c in children])
