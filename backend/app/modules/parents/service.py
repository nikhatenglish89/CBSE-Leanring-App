from sqlalchemy.orm import Session

from app.modules.classes import repository as classes_repo
from app.modules.parents.schemas import ChildProgressOut, PracticeAttemptOut
from app.modules.practice import repository as practice_repo
from app.modules.subjects import repository as subjects_repo
from app.modules.users import repository as users_repo
from app.modules.users.models import User

RECENT_ATTEMPTS_LIMIT = 5


def _attempt_out(db: Session, attempt) -> PracticeAttemptOut:
    practice_set = practice_repo.get_practice_set_by_id(db, attempt.practice_set_id)
    klass = classes_repo.get_class_by_id(db, practice_set.class_id) if practice_set else None
    subject = subjects_repo.get_subject_by_id(db, practice_set.subject_id) if practice_set else None
    return PracticeAttemptOut(
        id=attempt.id,
        practice_set_title=practice_set.title if practice_set else "Practice test",
        subject_name=subject.name if subject else "",
        class_name=klass.name if klass else "",
        score=attempt.score,
        total=attempt.total,
        created_at=attempt.created_at,
    )


def list_children_progress(db: Session, parent_user: User) -> list[ChildProgressOut]:
    parent_profile = users_repo.get_parent_profile_by_user_id(db, parent_user.id)
    if parent_profile is None:
        return []

    student_profiles = users_repo.list_students_for_parent_profile(db, parent_profile.id)
    rows: list[ChildProgressOut] = []
    for profile in student_profiles:
        student_user = users_repo.get_user_by_id(db, profile.user_id)
        if student_user is None:
            continue
        klass = classes_repo.get_class_by_id(db, profile.current_class_id) if profile.current_class_id else None
        tests_taken, average_score_pct, last_activity_at = practice_repo.attempt_stats_for_student(
            db, student_user.id
        )
        recent = practice_repo.list_attempts_for_student(db, student_user.id, limit=RECENT_ATTEMPTS_LIMIT)
        rows.append(
            ChildProgressOut(
                id=student_user.id,
                full_name=student_user.full_name,
                email=student_user.email,
                class_name=klass.name if klass else None,
                tests_taken=tests_taken,
                average_score_pct=average_score_pct,
                last_activity_at=last_activity_at,
                recent_attempts=[_attempt_out(db, a) for a in recent],
            )
        )
    rows.sort(key=lambda r: r.full_name)
    return rows
