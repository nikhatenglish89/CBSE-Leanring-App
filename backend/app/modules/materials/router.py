import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.materials import service as materials_service
from app.modules.materials.schemas import (
    LessonMaterialOut,
    MaterialBrowseOut,
    VideoBrowseOut,
    VideoOut,
    VideoSetRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1", tags=["materials"])


@router.get("/materials")
def browse_materials(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
) -> dict:
    rows, total = materials_service.browse_materials(
        db, pagination.offset, pagination.page_size, class_id=class_id, subject_id=subject_id
    )
    data = [MaterialBrowseOut.from_row(m, l, c).model_dump(mode="json") for m, l, c in rows]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.get("/videos")
def browse_videos(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
) -> dict:
    rows, total = materials_service.browse_videos(
        db, pagination.offset, pagination.page_size, class_id=class_id, subject_id=subject_id
    )
    data = [VideoBrowseOut.from_row(v, l, c).model_dump(mode="json") for v, l, c in rows]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.get("/lessons/{lesson_id}/materials")
def list_materials(lesson_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    items = materials_service.list_materials(db, current_user, lesson_id)
    return success([LessonMaterialOut.model_validate(m).model_dump(mode="json") for m in items])


@router.post("/lessons/{lesson_id}/materials", status_code=status.HTTP_201_CREATED)
async def upload_material(
    lesson_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()],
) -> dict:
    material = await materials_service.upload_material(db, current_user, lesson_id, file)
    return success(LessonMaterialOut.model_validate(material).model_dump(mode="json"))


@router.put("/materials/{material_id}")
async def replace_material(
    material_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()],
) -> dict:
    material = await materials_service.replace_material(db, current_user, material_id, file)
    return success(LessonMaterialOut.model_validate(material).model_dump(mode="json"))


@router.get("/materials/{material_id}/download")
def download_material(
    material_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> Response:
    material = materials_service.get_material_for_download(db, current_user, material_id)
    return Response(
        content=material.data,
        media_type=material.mime_type,
        headers={"Content-Disposition": f'inline; filename="{material.file_name}"'},
    )


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> None:
    materials_service.delete_material(db, current_user, material_id)


@router.get("/lessons/{lesson_id}/video")
def get_video(lesson_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    video = materials_service.get_video(db, current_user, lesson_id)
    return success(VideoOut.model_validate(video).model_dump(mode="json") if video else None)


@router.put("/lessons/{lesson_id}/video")
def set_video(
    lesson_id: uuid.UUID,
    payload: VideoSetRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    video = materials_service.set_video(db, current_user, lesson_id, payload)
    return success(VideoOut.model_validate(video).model_dump(mode="json"))


@router.delete("/lessons/{lesson_id}/video", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    lesson_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> None:
    materials_service.delete_video(db, current_user, lesson_id)
