import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GroupCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=2000)


class AddMemberRequest(BaseModel):
    student_id: uuid.UUID


class GroupTaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    due_date: datetime | None = None


class GroupMemberOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str

    @classmethod
    def from_row(cls, member, student) -> "GroupMemberOut":
        return cls(id=student.id, full_name=student.full_name, email=student.email)


class GroupTaskOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    due_date: datetime | None
    created_at: datetime

    @classmethod
    def from_row(cls, task) -> "GroupTaskOut":
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            created_at=task.created_at,
        )


class GroupOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    teacher_id: uuid.UUID
    member_count: int
    task_count: int
    created_at: datetime

    @classmethod
    def from_row(cls, group, member_count: int, task_count: int) -> "GroupOut":
        return cls(
            id=group.id,
            name=group.name,
            description=group.description,
            teacher_id=group.teacher_id,
            member_count=member_count,
            task_count=task_count,
            created_at=group.created_at,
        )


class GroupDetailOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    teacher_id: uuid.UUID
    teacher_name: str
    members: list[GroupMemberOut]
    tasks: list[GroupTaskOut]
    created_at: datetime

    @classmethod
    def from_row(cls, group, teacher, members: list[GroupMemberOut], tasks: list[GroupTaskOut]) -> "GroupDetailOut":
        return cls(
            id=group.id,
            name=group.name,
            description=group.description,
            teacher_id=group.teacher_id,
            teacher_name=teacher.full_name,
            members=members,
            tasks=tasks,
            created_at=group.created_at,
        )
