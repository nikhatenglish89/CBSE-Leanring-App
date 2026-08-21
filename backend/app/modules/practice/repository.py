import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.classes.models import Class
from app.modules.practice.models import PracticeQuestion, PracticeSet
from app.modules.subjects.models import Subject

_question_count_subq = (
    select(func.count(PracticeQuestion.id))
    .where(PracticeQuestion.practice_set_id == PracticeSet.id)
    .scalar_subquery()
)


def list_practice_sets(
    db: Session, *, class_id: uuid.UUID | None = None, subject_id: uuid.UUID | None = None
) -> list[tuple[PracticeSet, Class, Subject, int]]:
    stmt = (
        select(PracticeSet, Class, Subject, _question_count_subq)
        .join(Class, PracticeSet.class_id == Class.id)
        .join(Subject, PracticeSet.subject_id == Subject.id)
    )
    if class_id is not None:
        stmt = stmt.where(PracticeSet.class_id == class_id)
    if subject_id is not None:
        stmt = stmt.where(PracticeSet.subject_id == subject_id)
    stmt = stmt.order_by(Class.display_order, Subject.display_order, PracticeSet.display_order)
    return [tuple(row) for row in db.execute(stmt).all()]


def get_practice_set_by_id(db: Session, practice_set_id: uuid.UUID) -> PracticeSet | None:
    return db.get(PracticeSet, practice_set_id)


def get_practice_set_by_class_subject_title(
    db: Session, class_id: uuid.UUID, subject_id: uuid.UUID, title: str
) -> PracticeSet | None:
    return db.scalar(
        select(PracticeSet).where(
            PracticeSet.class_id == class_id,
            PracticeSet.subject_id == subject_id,
            PracticeSet.title == title,
        )
    )


def list_questions(db: Session, practice_set_id: uuid.UUID) -> list[PracticeQuestion]:
    stmt = (
        select(PracticeQuestion)
        .where(PracticeQuestion.practice_set_id == practice_set_id)
        .order_by(PracticeQuestion.display_order)
    )
    return list(db.scalars(stmt))


def create_practice_set(
    db: Session, *, class_id: uuid.UUID, subject_id: uuid.UUID, title: str, display_order: int
) -> PracticeSet:
    obj = PracticeSet(class_id=class_id, subject_id=subject_id, title=title, display_order=display_order)
    db.add(obj)
    db.flush()
    return obj


def create_questions(db: Session, practice_set_id: uuid.UUID, questions: list[dict]) -> None:
    for order, q in enumerate(questions):
        db.add(
            PracticeQuestion(
                practice_set_id=practice_set_id,
                question_text=q["question_text"],
                options=q["options"],
                correct_index=q["correct_index"],
                explanation=q.get("explanation", ""),
                display_order=order,
            )
        )
    db.commit()
