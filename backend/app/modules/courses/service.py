import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.classes import repository as classes_repo
from app.modules.courses import repository as courses_repo
from app.modules.courses.models import Course, CourseSection
from app.modules.courses.schemas import (
    CourseCreateRequest,
    CourseSectionCreateRequest,
    CourseSectionUpdateRequest,
    CourseUpdateRequest,
)
from app.modules.subjects import repository as subjects_repo
from app.modules.users import repository as users_repo
from app.modules.users.models import User

# Roles that can manage (and see the drafts of) *any* course, not just their own.
STAFF_ROLES = {"ADMIN", "SUPER_ADMIN", "CONTENT_MANAGER"}


def _is_staff(user: User) -> bool:
    return user.role.name in STAFF_ROLES


def assert_can_manage_course(db: Session, user: User, course: Course) -> None:
    """Shared ownership check, reused by the lessons module for
    section/lesson writes (a lesson's owner is its parent course's owner).
    """
    if _is_staff(user):
        return
    profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
    if profile is None or course.teacher_id != profile.id:
        raise AppError("PERMISSION_DENIED", "You do not have permission to do this.", 403)


def _resolve_teacher_id_for_create(db: Session, user: User, payload: CourseCreateRequest) -> uuid.UUID:
    if user.role.name == "TEACHER":
        profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
        if profile is None:
            raise AppError("TEACHER_PROFILE_MISSING", "No teacher profile found for this account.", 400)
        return profile.id
    if _is_staff(user):
        if payload.teacher_id is None:
            raise AppError(
                "TEACHER_ID_REQUIRED", "teacher_id is required when creating a course as staff.", 400
            )
        profile = users_repo.get_teacher_profile_by_id(db, payload.teacher_id)
        if profile is None:
            raise AppError("TEACHER_NOT_FOUND", "No teacher profile found for the given teacher_id.", 404)
        return profile.id
    raise AppError("PERMISSION_DENIED", "You do not have permission to do this.", 403)


def create_course(db: Session, user: User, payload: CourseCreateRequest) -> Course:
    if classes_repo.get_class_by_id(db, payload.class_id) is None:
        raise AppError("CLASS_NOT_FOUND", "Class not found.", 404)
    if subjects_repo.get_subject_by_id(db, payload.subject_id) is None:
        raise AppError("SUBJECT_NOT_FOUND", "Subject not found.", 404)
    teacher_id = _resolve_teacher_id_for_create(db, user, payload)
    return courses_repo.create_course(
        db,
        class_id=payload.class_id,
        subject_id=payload.subject_id,
        teacher_id=teacher_id,
        title=payload.title,
        description=payload.description,
        access_type=payload.access_type,
    )


def get_course_for_view(db: Session, user: User, course_id: uuid.UUID) -> Course:
    course = courses_repo.get_course_by_id(db, course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    if course.status == "PUBLISHED":
        return course
    # Draft courses are only visible to their owning teacher or staff — a
    # 404 (not 403) so a draft's existence isn't leaked to other students.
    if _is_staff(user):
        return course
    profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
    if profile is not None and course.teacher_id == profile.id:
        return course
    raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)


def list_courses(
    db: Session,
    user: User,
    offset: int,
    limit: int,
    *,
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    mine: bool = False,
) -> tuple[list[Course], int]:
    if mine:
        profile = users_repo.get_teacher_profile_by_user_id(db, user.id)
        if profile is None:
            return [], 0
        return courses_repo.list_courses(
            db, offset, limit, class_id=class_id, subject_id=subject_id, teacher_id=profile.id
        )
    status = None if _is_staff(user) else "PUBLISHED"
    return courses_repo.list_courses(db, offset, limit, status=status, class_id=class_id, subject_id=subject_id)


def update_course(db: Session, user: User, course_id: uuid.UUID, payload: CourseUpdateRequest) -> Course:
    course = courses_repo.get_course_by_id(db, course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    assert_can_manage_course(db, user, course)
    return courses_repo.update_course(
        db,
        course,
        title=payload.title,
        description=payload.description,
        access_type=payload.access_type,
        status=payload.status,
    )


def delete_course(db: Session, user: User, course_id: uuid.UUID) -> None:
    course = courses_repo.get_course_by_id(db, course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    assert_can_manage_course(db, user, course)
    courses_repo.soft_delete_course(db, course)


def create_section(
    db: Session, user: User, course_id: uuid.UUID, payload: CourseSectionCreateRequest
) -> CourseSection:
    course = courses_repo.get_course_by_id(db, course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    assert_can_manage_course(db, user, course)
    return courses_repo.create_section(
        db, course_id=course.id, title=payload.title, display_order=payload.display_order
    )


def list_sections(db: Session, user: User, course_id: uuid.UUID) -> list[CourseSection]:
    course = get_course_for_view(db, user, course_id)
    return courses_repo.list_sections(db, course.id)


def update_section(
    db: Session, user: User, section_id: uuid.UUID, payload: CourseSectionUpdateRequest
) -> CourseSection:
    section = courses_repo.get_section_by_id(db, section_id)
    if section is None:
        raise AppError("SECTION_NOT_FOUND", "Course section not found.", 404)
    course = courses_repo.get_course_by_id(db, section.course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    assert_can_manage_course(db, user, course)
    return courses_repo.update_section(db, section, title=payload.title, display_order=payload.display_order)


def delete_section(db: Session, user: User, section_id: uuid.UUID) -> None:
    section = courses_repo.get_section_by_id(db, section_id)
    if section is None:
        raise AppError("SECTION_NOT_FOUND", "Course section not found.", 404)
    course = courses_repo.get_course_by_id(db, section.course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    assert_can_manage_course(db, user, course)
    courses_repo.delete_section(db, section)
