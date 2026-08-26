import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.banners import repository as banners_repo
from app.modules.banners.models import Banner
from app.modules.banners.schemas import BannerUpdateRequest

# A homepage banner, not a lesson attachment — kept smaller than the
# general MAX_UPLOAD_BYTES in materials/service.py.
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


async def _read_and_validate_image(file: UploadFile) -> tuple[bytes, str]:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise AppError(
            "UNSUPPORTED_FILE_TYPE", "Only PNG, JPEG, or WEBP images are allowed.", 400
        )
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise AppError(
            "FILE_TOO_LARGE", f"Images must be under {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.", 400
        )
    if len(data) == 0:
        raise AppError("EMPTY_FILE", "The uploaded image is empty.", 400)
    return data, file.content_type


def list_public_banners(db: Session) -> list[Banner]:
    return banners_repo.list_active_banners(db)


def list_all_banners(db: Session) -> list[Banner]:
    return banners_repo.list_all_banners(db)


async def create_banner(
    db: Session, *, title: str, link_url: str, display_order: int, file: UploadFile
) -> Banner:
    data, mime_type = await _read_and_validate_image(file)
    return banners_repo.create_banner(
        db,
        title=title,
        link_url=link_url,
        display_order=display_order,
        image_mime_type=mime_type,
        image_data=data,
        is_active=True,
    )


def _get_banner_or_404(db: Session, banner_id: uuid.UUID) -> Banner:
    banner = banners_repo.get_banner_by_id(db, banner_id)
    if banner is None:
        raise AppError("BANNER_NOT_FOUND", "Banner not found.", 404)
    return banner


def update_banner(db: Session, banner_id: uuid.UUID, payload: BannerUpdateRequest) -> Banner:
    banner = _get_banner_or_404(db, banner_id)
    return banners_repo.update_banner(
        db,
        banner,
        title=payload.title,
        link_url=payload.link_url,
        display_order=payload.display_order,
        is_active=payload.is_active,
    )


def get_banner_image(db: Session, banner_id: uuid.UUID) -> Banner:
    return _get_banner_or_404(db, banner_id)


def delete_banner(db: Session, banner_id: uuid.UUID) -> None:
    banner = _get_banner_or_404(db, banner_id)
    banners_repo.delete_banner(db, banner)
