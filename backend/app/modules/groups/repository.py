import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.groups.models import Group, GroupMember, GroupTask, GroupTaskSubmission


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


def list_members(db: Session, group_id: uuid.UUID) -> list[GroupMember]:
    stmt = select(GroupMember).where(GroupMember.group_id == group_id).order_by(GroupMember.created_at.asc())
    return list(db.scalars(stmt))


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
    db: Session, *, task_id: uuid.UUID, student_id: uuid.UUID, content: str
) -> GroupTaskSubmission:
    existing = get_submission(db, task_id, student_id)
    if existing is not None:
        existing.content = content
        db.commit()
        db.refresh(existing)
        return existing
    submission = GroupTaskSubmission(task_id=task_id, student_id=student_id, content=content)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_submissions_for_task(db: Session, task_id: uuid.UUID) -> list[GroupTaskSubmission]:
    stmt = (
        select(GroupTaskSubmission)
        .where(GroupTaskSubmission.task_id == task_id)
        .order_by(GroupTaskSubmission.created_at.asc())
    )
    return list(db.scalars(stmt))


def count_submissions_for_task(db: Session, task_id: uuid.UUID) -> int:
    stmt = select(func.count()).select_from(GroupTaskSubmission).where(GroupTaskSubmission.task_id == task_id)
    return db.scalar(stmt) or 0
