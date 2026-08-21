"""Baseline CBSE curriculum reference data — Classes and Subjects.

Shared system/reference data, the same category as
app.modules.auth.seed.seed_roles_and_permissions: not user data, safe and
idempotent to run directly against production. It exists because this
platform deliberately has no admin account on production yet (see Phase 2
notes) to create this taxonomy by hand through the admin UI.
"""

from sqlalchemy.orm import Session

from app.modules.classes import repository as classes_repo
from app.modules.subjects import repository as subjects_repo

CORE_SUBJECTS = ["Mathematics", "Science", "English", "Hindi", "Social Science"]
# CBSE splits science into streams at XI-XII (Science/Commerce/Humanities);
# we seed a common cross-stream set rather than modeling streams, which is
# out of scope for this phase.
SENIOR_SUBJECTS = ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Computer Science"]

# Grade levels this platform covers per the frontend's "classes 6-12" tagline.
CLASS_SUBJECTS: list[tuple[str, list[str]]] = [
    ("Class VI", CORE_SUBJECTS),
    ("Class VII", CORE_SUBJECTS),
    ("Class VIII", CORE_SUBJECTS),
    ("Class IX", CORE_SUBJECTS),
    ("Class X", CORE_SUBJECTS),
    ("Class XI", SENIOR_SUBJECTS),
    ("Class XII", SENIOR_SUBJECTS),
]


def seed_academic_baseline(db: Session) -> None:
    """Idempotent: safe to call every app/test startup."""
    for order, (class_name, subjects) in enumerate(CLASS_SUBJECTS):
        klass = classes_repo.get_class_by_name(db, class_name)
        if klass is None:
            klass = classes_repo.create_class(db, name=class_name, display_order=order)
        for sub_order, subject_name in enumerate(subjects):
            if subjects_repo.get_subject_by_class_and_name(db, klass.id, subject_name) is None:
                subjects_repo.create_subject(
                    db, class_id=klass.id, name=subject_name, display_order=sub_order
                )
