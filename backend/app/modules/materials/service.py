import re
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.courses import repository as courses_repo
from app.modules.courses import service as courses_service
from app.modules.lessons import repository as lessons_repo
from app.modules.materials import repository as materials_repo
from app.modules.materials.models import LessonMaterial, Video
from app.modules.materials.schemas import VideoSetRequest
from app.modules.users import repository as users_repo
from app.modules.users.models import User

# Kept small on purpose — files are stored as bytes in Postgres (see the
# note in models.py), not in dedicated object storage.
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB

ALLOWED_MIME_TYPES: dict[str, str] = {
    "application/pdf": "PDF",
    "application/msword": "DOCUMENT",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCUMENT",
    "application/vnd.ms-powerpoint": "PRESENTATION",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PRESENTATION",
    "image/png": "IMAGE",
    "image/jpeg": "IMAGE",
    "image/webp": "IMAGE",
    "text/plain": "TEXT",
}

YOUTUBE_RE = re.compile(r"(youtube\.com|youtu\.be)", re.IGNORECASE)
VIMEO_RE = re.compile(r"vimeo\.com", re.IGNORECASE)


def _infer_video_provider(url: str) -> str:
    if YOUTUBE_RE.search(url):
        return "YOUTUBE"
    if VIMEO_RE.search(url):
        return "VIMEO"
    return "URL"


def _get_lesson_and_course(db: Session, lesson_id: uuid.UUID):
    lesson = lessons_repo.get_lesson_by_id(db, lesson_id)
    if lesson is None:
        raise AppError("LESSON_NOT_FOUND", "Lesson not found.", 404)
    section = courses_repo.get_section_by_id(db, lesson.course_section_id)
    if section is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    course = courses_repo.get_course_by_id(db, section.course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    return lesson, course


async def _read_and_validate_upload(file: UploadFile) -> tuple[bytes, str]:
    if file.content_type not in ALLOWED_MIME_TYPES:
        allowed = ", ".join(sorted(set(ALLOWED_MIME_TYPES.values())))
        raise AppError(
            "UNSUPPORTED_FILE_TYPE", f"That file type isn't supported. Allowed: {allowed}.", 400
        )
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise AppError(
            "FILE_TOO_LARGE", f"Files must be under {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.", 400
        )
    if len(data) == 0:
        raise AppError("EMPTY_FILE", "The uploaded file is empty.", 400)
    return data, ALLOWED_MIME_TYPES[file.content_type]


def list_materials(db: Session, user: User, lesson_id: uuid.UUID) -> list[LessonMaterial]:
    _lesson, course = _get_lesson_and_course(db, lesson_id)
    courses_service.get_course_for_view(db, user, course.id)
    return materials_repo.list_materials(db, lesson_id)


async def upload_material(
    db: Session, user: User, lesson_id: uuid.UUID, file: UploadFile
) -> LessonMaterial:
    _lesson, course = _get_lesson_and_course(db, lesson_id)
    courses_service.assert_can_manage_course(db, user, course)
    data, material_type = await _read_and_validate_upload(file)
    return materials_repo.create_material(
        db,
        lesson_id=lesson_id,
        material_type=material_type,
        file_name=file.filename or "upload",
        mime_type=file.content_type,
        file_size=len(data),
        data=data,
    )


def _get_material_and_course(db: Session, material_id: uuid.UUID):
    material = materials_repo.get_material_by_id(db, material_id)
    if material is None:
        raise AppError("MATERIAL_NOT_FOUND", "Material not found.", 404)
    _lesson, course = _get_lesson_and_course(db, material.lesson_id)
    return material, course


async def replace_material(
    db: Session, user: User, material_id: uuid.UUID, file: UploadFile
) -> LessonMaterial:
    material, course = _get_material_and_course(db, material_id)
    courses_service.assert_can_manage_course(db, user, course)
    data, material_type = await _read_and_validate_upload(file)
    return materials_repo.replace_material_file(
        db,
        material,
        file_name=file.filename or material.file_name,
        mime_type=file.content_type,
        file_size=len(data),
        data=data,
        material_type=material_type,
    )


def get_material_for_download(db: Session, user: User, material_id: uuid.UUID) -> LessonMaterial:
    material, course = _get_material_and_course(db, material_id)
    courses_service.get_course_for_view(db, user, course.id)
    return material


def delete_material(db: Session, user: User, material_id: uuid.UUID) -> None:
    material, course = _get_material_and_course(db, material_id)
    courses_service.assert_can_manage_course(db, user, course)
    materials_repo.delete_material(db, material)


def get_video(db: Session, user: User, lesson_id: uuid.UUID) -> Video | None:
    _lesson, course = _get_lesson_and_course(db, lesson_id)
    courses_service.get_course_for_view(db, user, course.id)
    return materials_repo.get_video_by_lesson_id(db, lesson_id)


def set_video(db: Session, user: User, lesson_id: uuid.UUID, payload: VideoSetRequest) -> Video:
    _lesson, course = _get_lesson_and_course(db, lesson_id)
    courses_service.assert_can_manage_course(db, user, course)
    provider = _infer_video_provider(payload.url)
    existing = materials_repo.get_video_by_lesson_id(db, lesson_id)
    if existing is None:
        return materials_repo.create_video(
            db, lesson_id=lesson_id, provider=provider, provider_ref=payload.url, title=payload.title
        )
    return materials_repo.update_video(db, existing, provider=provider, provider_ref=payload.url, title=payload.title)


def delete_video(db: Session, user: User, lesson_id: uuid.UUID) -> None:
    _lesson, course = _get_lesson_and_course(db, lesson_id)
    courses_service.assert_can_manage_course(db, user, course)
    existing = materials_repo.get_video_by_lesson_id(db, lesson_id)
    if existing is None:
        raise AppError("VIDEO_NOT_FOUND", "This lesson has no video.", 404)
    materials_repo.delete_video(db, existing)


# Students/parents only ever see materials from published courses (same
# rule as the course catalog). Teachers and staff see everything, drafts
# included and regardless of who owns the course — a teacher building a
# lesson can see what materials colleagues have uploaded elsewhere, even
# before they publish, instead of only their own courses.
_LEARNER_ROLES = {"STUDENT", "PARENT"}


def _only_free_for_learner(db: Session, user: User) -> bool:
    # Only students carry the admin-verification gate — an unverified
    # student sees FREE published content only, same rule as the course
    # catalog/detail view. Parents aren't gated (no verification concept
    # for them yet), matching the scope of the original request.
    if user.role.name != "STUDENT":
        return False
    profile = users_repo.get_student_profile_by_user_id(db, user.id)
    return not (profile and profile.verified)


def browse_materials(
    db: Session, user: User, offset: int, limit: int, *, class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
):
    include_drafts = user.role.name not in _LEARNER_ROLES
    only_free = _only_free_for_learner(db, user)
    return materials_repo.browse_materials(
        db, offset, limit, include_drafts=include_drafts, only_free=only_free,
        class_id=class_id, subject_id=subject_id,
    )


def browse_videos(
    db: Session, user: User, offset: int, limit: int, *, class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
):
    include_drafts = user.role.name not in _LEARNER_ROLES
    only_free = _only_free_for_learner(db, user)
    return materials_repo.browse_videos(
        db, offset, limit, include_drafts=include_drafts, only_free=only_free,
        class_id=class_id, subject_id=subject_id,
    )
