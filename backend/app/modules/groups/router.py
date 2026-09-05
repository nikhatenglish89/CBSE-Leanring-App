import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser
from app.modules.groups import service as groups_service
from app.modules.groups.schemas import (
    AddMemberRequest,
    GroupCreateRequest,
    GroupDetailOut,
    GroupOut,
    GroupTaskCreateRequest,
    GroupTaskOut,
    TaskSubmissionOut,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/groups", tags=["groups"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreateRequest, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    group = groups_service.create_group(db, current_user, payload)
    return success(GroupOut.from_row(group, 0, 0).model_dump(mode="json"))


@router.get("/mine")
def list_my_groups(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    if current_user.role.name == "TEACHER":
        rows = groups_service.list_groups_for_teacher(db, current_user)
    elif current_user.role.name == "STUDENT":
        rows = groups_service.list_groups_for_student(db, current_user)
    else:
        rows = []
    data = [GroupOut.from_row(g, member_count, task_count).model_dump(mode="json") for g, member_count, task_count in rows]
    return success(data)


@router.get("/{group_id}")
def get_group_detail(
    group_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    group, teacher, members, tasks = groups_service.get_group_detail_row(db, current_user, group_id)
    return success(GroupDetailOut.from_row(group, teacher, members, tasks).model_dump(mode="json"))


@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    group_id: uuid.UUID,
    payload: AddMemberRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    groups_service.add_member(db, current_user, group_id, payload.student_id)
    return success({"added": True})


@router.delete("/{group_id}/members/{student_id}")
def remove_member(
    group_id: uuid.UUID, student_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    groups_service.remove_member(db, current_user, group_id, student_id)
    return success({"removed": True})


@router.post("/{group_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    group_id: uuid.UUID,
    payload: GroupTaskCreateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    task = groups_service.create_task(
        db, current_user, group_id, title=payload.title, description=payload.description, due_date=payload.due_date
    )
    return success(GroupTaskOut.from_row(task).model_dump(mode="json"))


@router.post("/{group_id}/tasks/{task_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_task(
    group_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    content: Annotated[str, Form()] = "",
    file: Annotated[UploadFile | None, File()] = None,
) -> dict:
    submission = await groups_service.submit_task(db, current_user, group_id, task_id, content=content, file=file)
    return success(TaskSubmissionOut.from_row(submission, current_user).model_dump(mode="json"))


@router.get("/{group_id}/tasks/{task_id}/submissions")
def list_task_submissions(
    group_id: uuid.UUID, task_id: uuid.UUID, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    rows = groups_service.list_task_submissions(db, current_user, group_id, task_id)
    return success([r.model_dump(mode="json") for r in rows])


@router.get("/{group_id}/tasks/{task_id}/submissions/{submission_id}/file")
def download_submission_file(
    group_id: uuid.UUID,
    task_id: uuid.UUID,
    submission_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    submission = groups_service.get_submission_file(db, current_user, group_id, task_id, submission_id)
    return Response(
        content=submission.file_data,
        media_type=submission.file_mime_type,
        headers={"Content-Disposition": f'attachment; filename="{submission.file_name}"'},
    )
