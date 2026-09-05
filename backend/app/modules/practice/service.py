import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.classes import repository as classes_repo
from app.modules.practice import repository as practice_repo
from app.modules.practice.schemas import PracticeQuestionResult, PracticeSubmitRequest
from app.modules.subjects import repository as subjects_repo


def list_practice_sets(db: Session, *, class_id: uuid.UUID | None = None, subject_id: uuid.UUID | None = None):
    return practice_repo.list_practice_sets(db, class_id=class_id, subject_id=subject_id)


def get_practice_set_detail(db: Session, practice_set_id: uuid.UUID):
    practice_set = practice_repo.get_practice_set_by_id(db, practice_set_id)
    if practice_set is None:
        raise AppError("PRACTICE_SET_NOT_FOUND", "Practice set not found.", 404)
    klass = classes_repo.get_class_by_id(db, practice_set.class_id)
    subject = subjects_repo.get_subject_by_id(db, practice_set.subject_id)
    questions = practice_repo.list_questions(db, practice_set.id)
    return practice_set, klass, subject, questions


def submit_practice_set(
    db: Session, practice_set_id: uuid.UUID, student_id: uuid.UUID, payload: PracticeSubmitRequest
) -> tuple[int, int, list[PracticeQuestionResult]]:
    practice_set = practice_repo.get_practice_set_by_id(db, practice_set_id)
    if practice_set is None:
        raise AppError("PRACTICE_SET_NOT_FOUND", "Practice set not found.", 404)
    questions = practice_repo.list_questions(db, practice_set.id)
    selected_by_question = {a.question_id: a.selected_index for a in payload.answers}

    score = 0
    results: list[PracticeQuestionResult] = []
    for question in questions:
        selected = selected_by_question.get(question.id)
        is_correct = selected is not None and selected == question.correct_index
        if is_correct:
            score += 1
        results.append(
            PracticeQuestionResult(
                question_id=question.id,
                question_text=question.question_text,
                options=question.options,
                correct_index=question.correct_index,
                selected_index=selected,
                is_correct=is_correct,
                explanation=question.explanation,
            )
        )
    # Persisted so a parent's progress view (and any future analytics) has
    # real history instead of a result that only ever existed in-memory.
    practice_repo.create_attempt(
        db, student_id=student_id, practice_set_id=practice_set.id, score=score, total=len(questions)
    )
    return score, len(questions), results
