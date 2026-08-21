import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.courses import repository as courses_repo
from app.modules.courses import service as courses_service
from app.modules.courses.models import Course, CourseSection
from app.modules.lessons import repository as lessons_repo
from app.modules.lessons.models import Lesson
from app.modules.lessons.schemas import LessonCreateRequest, LessonUpdateRequest
from app.modules.subjects import repository as subjects_repo
from app.modules.users.models import User


def _get_section_or_404(db: Session, section_id: uuid.UUID) -> CourseSection:
    section = courses_repo.get_section_by_id(db, section_id)
    if section is None:
        raise AppError("SECTION_NOT_FOUND", "Course section not found.", 404)
    return section


def _get_course_for_section(db: Session, section: CourseSection) -> Course:
    course = courses_repo.get_course_by_id(db, section.course_id)
    if course is None:
        raise AppError("COURSE_NOT_FOUND", "Course not found.", 404)
    return course


def _get_lesson_or_404(db: Session, lesson_id: uuid.UUID) -> Lesson:
    lesson = lessons_repo.get_lesson_by_id(db, lesson_id)
    if lesson is None:
        raise AppError("LESSON_NOT_FOUND", "Lesson not found.", 404)
    return lesson


def list_lessons(db: Session, user: User, section_id: uuid.UUID) -> list[Lesson]:
    section = _get_section_or_404(db, section_id)
    course = _get_course_for_section(db, section)
    # Reuses the parent course's own visibility rule (published, or owner/staff).
    courses_service.get_course_for_view(db, user, course.id)
    return lessons_repo.list_lessons(db, section_id)


def create_lesson(db: Session, user: User, section_id: uuid.UUID, payload: LessonCreateRequest) -> Lesson:
    section = _get_section_or_404(db, section_id)
    course = _get_course_for_section(db, section)
    courses_service.assert_can_manage_course(db, user, course)
    if payload.chapter_id is not None and subjects_repo.get_chapter_by_id(db, payload.chapter_id) is None:
        raise AppError("CHAPTER_NOT_FOUND", "Chapter not found.", 404)
    return lessons_repo.create_lesson(
        db,
        course_section_id=section.id,
        chapter_id=payload.chapter_id,
        title=payload.title,
        description=payload.description,
        content=payload.content,
        content_type=payload.content_type,
        display_order=payload.display_order,
    )


def get_lesson(db: Session, user: User, lesson_id: uuid.UUID) -> Lesson:
    lesson = _get_lesson_or_404(db, lesson_id)
    section = _get_section_or_404(db, lesson.course_section_id)
    course = _get_course_for_section(db, section)
    courses_service.get_course_for_view(db, user, course.id)
    return lesson


def update_lesson(db: Session, user: User, lesson_id: uuid.UUID, payload: LessonUpdateRequest) -> Lesson:
    lesson = _get_lesson_or_404(db, lesson_id)
    section = _get_section_or_404(db, lesson.course_section_id)
    course = _get_course_for_section(db, section)
    courses_service.assert_can_manage_course(db, user, course)
    return lessons_repo.update_lesson(
        db,
        lesson,
        title=payload.title,
        description=payload.description,
        content=payload.content,
        content_type=payload.content_type,
        display_order=payload.display_order,
    )


def delete_lesson(db: Session, user: User, lesson_id: uuid.UUID) -> None:
    lesson = _get_lesson_or_404(db, lesson_id)
    section = _get_section_or_404(db, lesson.course_section_id)
    course = _get_course_for_section(db, section)
    courses_service.assert_can_manage_course(db, user, course)
    lessons_repo.soft_delete_lesson(db, lesson)
