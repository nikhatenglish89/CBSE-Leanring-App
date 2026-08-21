"""Baseline CBSE practice-test content — 20-question sets per class+subject.

Same category as app.modules.classes.seed.seed_academic_baseline: reference
curriculum content owned by the platform, not user data, safe and idempotent
to run directly against production.
"""

from sqlalchemy.orm import Session

from app.modules.classes import repository as classes_repo
from app.modules.practice import repository as practice_repo
from app.modules.practice.seed_data import (
    class_ix,
    class_vi,
    class_vii,
    class_viii,
    class_x,
    class_xi,
    class_xii,
)
from app.modules.subjects import repository as subjects_repo

CLASS_DATA: list[tuple[str, dict[str, list[dict]]]] = [
    ("Class VI", class_vi.QUESTIONS),
    ("Class VII", class_vii.QUESTIONS),
    ("Class VIII", class_viii.QUESTIONS),
    ("Class IX", class_ix.QUESTIONS),
    ("Class X", class_x.QUESTIONS),
    ("Class XI", class_xi.QUESTIONS),
    ("Class XII", class_xii.QUESTIONS),
]


def seed_practice_sets(db: Session) -> None:
    """Idempotent: safe to call every app/test startup."""
    for class_name, subjects in CLASS_DATA:
        klass = classes_repo.get_class_by_name(db, class_name)
        if klass is None:
            continue
        for order, (subject_name, questions) in enumerate(subjects.items()):
            subject = subjects_repo.get_subject_by_class_and_name(db, klass.id, subject_name)
            if subject is None:
                continue
            title = f"{subject_name} Practice Set"
            if practice_repo.get_practice_set_by_class_subject_title(db, klass.id, subject.id, title):
                continue
            practice_set = practice_repo.create_practice_set(
                db, class_id=klass.id, subject_id=subject.id, title=title, display_order=order
            )
            practice_repo.create_questions(db, practice_set.id, questions)
