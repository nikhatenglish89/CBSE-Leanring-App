import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.modules.classes.models import Class
from app.modules.courses.models import Course, CourseSection
from app.modules.interaction.models import Answer, LiveClass, Question
from app.modules.lessons.models import Lesson
from app.modules.subjects.models import Subject
from app.modules.users.models import TeacherProfile, User

# --- Questions & answers -----------------------------------------------


def create_question(db: Session, *, lesson_id: uuid.UUID, student_id: uuid.UUID, body: str) -> Question:
    obj = Question(lesson_id=lesson_id, student_id=student_id, body=body)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_question_by_id(db: Session, question_id: uuid.UUID) -> Question | None:
    return db.get(Question, question_id)


def get_answer_by_question_id(db: Session, question_id: uuid.UUID) -> Answer | None:
    return db.scalar(select(Answer).where(Answer.question_id == question_id))


def upsert_answer(db: Session, *, question_id: uuid.UUID, teacher_id: uuid.UUID, body: str) -> Answer:
    existing = get_answer_by_question_id(db, question_id)
    if existing is not None:
        existing.teacher_id = teacher_id
        existing.body = body
        db.commit()
        db.refresh(existing)
        return existing
    obj = Answer(question_id=question_id, teacher_id=teacher_id, body=body)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_questions_for_lesson(
    db: Session, lesson_id: uuid.UUID
) -> list[tuple[Question, User, Answer | None, User | None]]:
    asker = aliased(User)
    answerer = aliased(User)
    stmt = (
        select(Question, asker, Answer, answerer)
        .join(asker, Question.student_id == asker.id)
        .outerjoin(Answer, Answer.question_id == Question.id)
        .outerjoin(answerer, Answer.teacher_id == answerer.id)
        .where(Question.lesson_id == lesson_id)
        .order_by(Question.created_at)
    )
    return [tuple(row) for row in db.execute(stmt).all()]


def browse_questions(
    db: Session,
    offset: int,
    limit: int,
    *,
    include_drafts: bool,
    only_free: bool = False,
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    answered: bool | None = None,
    student_id: uuid.UUID | None = None,
) -> tuple[list[tuple[Question, User, Answer | None, User | None, Lesson, Course, Class, Subject]], int]:
    asker = aliased(User)
    answerer = aliased(User)
    stmt = (
        select(Question, asker, Answer, answerer, Lesson, Course, Class, Subject)
        .join(asker, Question.student_id == asker.id)
        .outerjoin(Answer, Answer.question_id == Question.id)
        .outerjoin(answerer, Answer.teacher_id == answerer.id)
        .join(Lesson, Question.lesson_id == Lesson.id)
        .join(CourseSection, Lesson.course_section_id == CourseSection.id)
        .join(Course, CourseSection.course_id == Course.id)
        .join(Class, Course.class_id == Class.id)
        .join(Subject, Course.subject_id == Subject.id)
        .where(Course.deleted_at.is_(None), Lesson.deleted_at.is_(None))
    )
    if not include_drafts:
        stmt = stmt.where(Course.status == "PUBLISHED")
    if only_free:
        stmt = stmt.where(Course.access_type == "FREE")
    if class_id is not None:
        stmt = stmt.where(Course.class_id == class_id)
    if subject_id is not None:
        stmt = stmt.where(Course.subject_id == subject_id)
    if answered is True:
        stmt = stmt.where(Answer.id.is_not(None))
    elif answered is False:
        stmt = stmt.where(Answer.id.is_(None))
    if student_id is not None:
        stmt = stmt.where(Question.student_id == student_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(
        stmt.order_by(Question.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [tuple(row) for row in rows], total


# --- Live classes ---------------------------------------------------------


def create_live_class(db: Session, **fields) -> LiveClass:
    obj = LiveClass(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_live_class_by_id(db: Session, live_class_id: uuid.UUID) -> LiveClass | None:
    return db.get(LiveClass, live_class_id)


def get_live_class_context(db: Session, live_class: LiveClass) -> tuple[Class, Subject, User] | None:
    """Resolves the class/subject/teacher-user needed to build a LiveClassOut
    for a single already-fetched LiveClass row. Independent lookups rather
    than one join — the FK ids don't share a natural join chain (there's no
    join condition linking Class and Subject to each other directly)."""
    klass = db.get(Class, live_class.class_id)
    subject = db.get(Subject, live_class.subject_id)
    profile = db.get(TeacherProfile, live_class.teacher_id)
    if klass is None or subject is None or profile is None:
        return None
    teacher = db.get(User, profile.user_id)
    if teacher is None:
        return None
    return klass, subject, teacher


def update_live_class(
    db: Session,
    obj: LiveClass,
    *,
    title: str | None,
    description: str | None,
    scheduled_at: datetime | None,
    meeting_url: str | None,
) -> LiveClass:
    if title is not None:
        obj.title = title
    if description is not None:
        obj.description = description
    if scheduled_at is not None:
        obj.scheduled_at = scheduled_at
    if meeting_url is not None:
        obj.meeting_url = meeting_url
    db.commit()
    db.refresh(obj)
    return obj


def delete_live_class(db: Session, obj: LiveClass) -> None:
    db.delete(obj)
    db.commit()


def browse_live_classes(
    db: Session,
    offset: int,
    limit: int,
    *,
    class_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    upcoming_only: bool = False,
    now: datetime | None = None,
) -> tuple[list[tuple[LiveClass, Class, Subject, User]], int]:
    stmt = (
        select(LiveClass, Class, Subject, User)
        .join(Class, LiveClass.class_id == Class.id)
        .join(Subject, LiveClass.subject_id == Subject.id)
        .join(TeacherProfile, LiveClass.teacher_id == TeacherProfile.id)
        .join(User, TeacherProfile.user_id == User.id)
    )
    if class_id is not None:
        stmt = stmt.where(LiveClass.class_id == class_id)
    if subject_id is not None:
        stmt = stmt.where(LiveClass.subject_id == subject_id)
    if upcoming_only and now is not None:
        stmt = stmt.where(LiveClass.scheduled_at >= now)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(
        stmt.order_by(LiveClass.scheduled_at).offset(offset).limit(limit)
    ).all()
    return [tuple(row) for row in rows], total
