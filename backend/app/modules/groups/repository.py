import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.groups.models import Group, GroupMember, GroupTask, GroupTaskSubmission
from app.modules.users.models import User


def create_group(db: Session, *, teacher_id: uuid.UUID, name: str, description: str) -> Group:
    group = Group(teacher_id=teacher_id, name=name, description=description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def get_group_by_id(db: Session, group_id: uuid.UUID) -> Group | None:
    return db.get(Group, group_id)


def list_groups_for_teacher(db: Session, teacher_id: uuid.UUID) -> list[Group]:
    stmt = select(Group).where(Group.teacher_id == teacher_id).order_by(Group.created_at.desc())
    return list(db.scalars(stmt))


def list_groups_for_student(db: Session, student_id: uuid.UUID) -> list[Group]:
    stmt = (
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.student_id == student_id)
        .order_by(Group.created_at.desc())
    )
    return list(db.scalars(stmt))


def count_members(db: Session, group_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)) or 0


def count_tasks(db: Session, group_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(GroupTask).where(GroupTask.group_id == group_id)) or 0


def get_member(db: Session, group_id: uuid.UUID, student_id: uuid.UUID) -> GroupMember | None:
    stmt = select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.student_id == student_id)
    return db.scalar(stmt)


def add_member(db: Session, *, group_id: uuid.UUID, student_id: uuid.UUID) -> GroupMember:
    member = GroupMember(group_id=group_id, student_id=student_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_member(db: Session, member: GroupMember) -> None:
    db.delete(member)
    db.commit()


def list_members_with_students(db: Session, group_id: uuid.UUID) -> list[tuple[GroupMember, User]]:
    """Members joined to their user row in one query — avoids an N+1
    get_user_by_id call per student, which made loading a full class-sized
    group visibly slow (or effectively hang) as membership grew."""
    stmt = (
        select(GroupMember, User)
        .join(User, User.id == GroupMember.student_id)
        .where(GroupMember.group_id == group_id)
        .order_by(GroupMember.created_at.asc())
    )
    return [(member, student) for member, student in db.execute(stmt).all()]


def create_task(
    db: Session, *, group_id: uuid.UUID, title: str, description: str, due_date: datetime | None
) -> GroupTask:
    task = GroupTask(group_id=group_id, title=title, description=description, due_date=due_date)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, group_id: uuid.UUID) -> list[GroupTask]:
    stmt = select(GroupTask).where(GroupTask.group_id == group_id).order_by(GroupTask.created_at.desc())
    return list(db.scalars(stmt))


def get_task_by_id(db: Session, task_id: uuid.UUID) -> GroupTask | None:
    return db.get(GroupTask, task_id)


def get_submission(db: Session, task_id: uuid.UUID, student_id: uuid.UUID) -> GroupTaskSubmission | None:
    stmt = select(GroupTaskSubmission).where(
        GroupTaskSubmission.task_id == task_id, GroupTaskSubmission.student_id == student_id
    )
    return db.scalar(stmt)


def upsert_submission(
    db: Session,
    *,
    task_id: uuid.UUID,
    student_id: uuid.UUID,
    content: str,
    file_name: str | None = None,
    file_mime_type: str | None = None,
    file_size: int | None = None,
    file_data: bytes | None = None,
) -> GroupTaskSubmission:
    existing = get_submission(db, task_id, student_id)
    if existing is not None:
        existing.content = content
        # A resubmission without a new file keeps whatever was already
        # attached, rather than silently dropping it.
        if file_data is not None:
            existing.file_name = file_name
            existing.file_mime_type = file_mime_type
            existing.file_size = file_size
            existing.file_data = file_data
        db.commit()
        db.refresh(existing)
        return existing
    submission = GroupTaskSubmission(
        task_id=task_id,
        student_id=student_id,
        content=content,
        file_name=file_name,
        file_mime_type=file_mime_type,
        file_size=file_size,
        file_data=file_data,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_submission_by_id(db: Session, submission_id: uuid.UUID) -> GroupTaskSubmission | None:
    return db.get(GroupTaskSubmission, submission_id)


def list_submissions_for_task(db: Session, task_id: uuid.UUID) -> list[GroupTaskSubmission]:
    stmt = (
        select(GroupTaskSubmission)
        .where(GroupTaskSubmission.task_id == task_id)
        .order_by(GroupTaskSubmission.created_at.asc())
    )
    return list(db.scalars(stmt))


def count_submissions_by_task(db: Session, task_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    """Submission counts for every task in one query, instead of one
    count call per task on the group detail page."""
    if not task_ids:
        return {}
    stmt = (
        select(GroupTaskSubmission.task_id, func.count())
        .where(GroupTaskSubmission.task_id.in_(task_ids))
        .group_by(GroupTaskSubmission.task_id)
    )
    return dict(db.execute(stmt).all())


def get_submissions_for_student(
    db: Session, task_ids: list[uuid.UUID], student_id: uuid.UUID
) -> dict[uuid.UUID, GroupTaskSubmission]:
    """A student's own submissions across every task in one query, instead
    of one get_submission call per task on the group detail page."""
    if not task_ids:
        return {}
    stmt = select(GroupTaskSubmission).where(
        GroupTaskSubmission.task_id.in_(task_ids), GroupTaskSubmission.student_id == student_id
    )
    return {s.task_id: s for s in db.scalars(stmt)}
