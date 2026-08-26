import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.modules.banners import service as banners_service
from app.modules.banners.schemas import BannerOut, BannerUpdateRequest
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/banners", tags=["banners"])


@router.get("/public")
def list_public_banners(db: Annotated[Session, Depends(get_db)]) -> dict:
    """No auth required — this feeds the public home page."""
    items = banners_service.list_public_banners(db)
    return success([BannerOut.model_validate(b).model_dump(mode="json") for b in items])


@router.get("", dependencies=[Depends(require_permission("banner:manage"))])
def list_all_banners(db: Annotated[Session, Depends(get_db)]) -> dict:
    items = banners_service.list_all_banners(db)
    return success([BannerOut.model_validate(b).model_dump(mode="json") for b in items])


@router.post(
    "", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("banner:manage"))]
)
async def create_banner(
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    link_url: Annotated[str, Form()] = "",
    display_order: Annotated[int, Form()] = 0,
) -> dict:
    banner = await banners_service.create_banner(
        db, title=title, link_url=link_url, display_order=display_order, file=file
    )
    return success(BannerOut.model_validate(banner).model_dump(mode="json"))


@router.patch("/{banner_id}", dependencies=[Depends(require_permission("banner:manage"))])
def update_banner(
    banner_id: uuid.UUID, payload: BannerUpdateRequest, db: Annotated[Session, Depends(get_db)]
) -> dict:
    banner = banners_service.update_banner(db, banner_id, payload)
    return success(BannerOut.model_validate(banner).model_dump(mode="json"))


@router.delete(
    "/{banner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("banner:manage"))],
)
def delete_banner(banner_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> None:
    banners_service.delete_banner(db, banner_id)


@router.get("/{banner_id}/image")
def get_banner_image(banner_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> Response:
    """No auth required — an <img> tag on the public home page hits this
    directly, so it can't carry an Authorization header."""
    banner = banners_service.get_banner_image(db, banner_id)
    return Response(content=banner.image_data, media_type=banner.image_mime_type)
