import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.groups import repository as groups_repo
from app.modules.groups.models import Group, GroupTask
from app.modules.groups.schemas import GroupCreateRequest, GroupMemberOut, GroupTaskOut
from app.modules.users import repository as users_repo
from app.modules.users.models import User


def create_group(db: Session, teacher: User, payload: GroupCreateRequest) -> Group:
    if teacher.role.name != "TEACHER":
        raise AppError("PERMISSION_DENIED", "Only teachers can create groups.", 403)
    profile = users_repo.get_teacher_profile_by_user_id(db, teacher.id)
    if profile is None or not profile.verified:
        raise AppError("TEACHER_NOT_VERIFIED", "Your teacher account hasn't been approved by an admin yet.", 403)
    return groups_repo.create_group(db, teacher_id=teacher.id, name=payload.name, description=payload.description)


def _get_owned_group(db: Session, teacher: User, group_id: uuid.UUID) -> Group:
    group = groups_repo.get_group_by_id(db, group_id)
    if group is None or group.teacher_id != teacher.id:
        raise AppError("GROUP_NOT_FOUND", "Group not found.", 404)
    return group


def _is_member(db: Session, group_id: uuid.UUID, student_id: uuid.UUID) -> bool:
    return groups_repo.get_member(db, group_id, student_id) is not None


def get_group_detail_row(db: Session, user: User, group_id: uuid.UUID):
    group = groups_repo.get_group_by_id(db, group_id)
    if group is None:
        raise AppError("GROUP_NOT_FOUND", "Group not found.", 404)
    is_owner = group.teacher_id == user.id
    if not is_owner and not _is_member(db, group_id, user.id):
        raise AppError("GROUP_NOT_FOUND", "Group not found.", 404)

    teacher = users_repo.get_user_by_id(db, group.teacher_id)
    member_rows = groups_repo.list_members(db, group_id)
    students = [users_repo.get_user_by_id(db, m.student_id) for m in member_rows]
    members = [GroupMemberOut.from_row(m, s) for m, s in zip(member_rows, students) if s is not None]
    tasks = [GroupTaskOut.from_row(t) for t in groups_repo.list_tasks(db, group_id)]
    return group, teacher, members, tasks


def list_groups_for_teacher(db: Session, teacher: User):
    groups = groups_repo.list_groups_for_teacher(db, teacher.id)
    return [(g, groups_repo.count_members(db, g.id), groups_repo.count_tasks(db, g.id)) for g in groups]


def list_groups_for_student(db: Session, student: User):
    groups = groups_repo.list_groups_for_student(db, student.id)
    return [(g, groups_repo.count_members(db, g.id), groups_repo.count_tasks(db, g.id)) for g in groups]


def add_member(db: Session, teacher: User, group_id: uuid.UUID, student_id: uuid.UUID) -> None:
    group = _get_owned_group(db, teacher, group_id)
    student = users_repo.get_user_by_id(db, student_id)
    if student is None or student.role.name != "STUDENT":
        raise AppError("STUDENT_NOT_FOUND", "Student not found.", 404)
    if groups_repo.get_member(db, group.id, student_id) is not None:
        raise AppError("ALREADY_MEMBER", "This student is already in the group.", 409)
    groups_repo.add_member(db, group_id=group.id, student_id=student_id)


def remove_member(db: Session, teacher: User, group_id: uuid.UUID, student_id: uuid.UUID) -> None:
    group = _get_owned_group(db, teacher, group_id)
    member = groups_repo.get_member(db, group.id, student_id)
    if member is None:
        raise AppError("MEMBER_NOT_FOUND", "This student is not in the group.", 404)
    groups_repo.remove_member(db, member)


def create_task(
    db: Session, teacher: User, group_id: uuid.UUID, *, title: str, description: str, due_date: datetime | None
) -> GroupTask:
    group = _get_owned_group(db, teacher, group_id)
    return groups_repo.create_task(db, group_id=group.id, title=title, description=description, due_date=due_date)
