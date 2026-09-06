import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.groups import repository as groups_repo
from app.modules.groups.models import Group, GroupTask, GroupTaskSubmission
from app.modules.groups.schemas import GroupCreateRequest, GroupMemberOut, GroupTaskOut, TaskSubmissionOut
from app.modules.users import repository as users_repo
from app.modules.users.models import User

# Kept small on purpose — files are stored as bytes in Postgres (see the
# note in models.py), not in dedicated object storage.
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB

ALLOWED_SUBMISSION_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/png",
    "image/jpeg",
    "image/webp",
}

# Browsers are unreliable about the Content-Type they report for a file
# input — Windows commonly reports .doc as application/octet-stream when
# no app is registered for it, some browsers append "; charset=utf-8" to
# text/plain, and a missing OS extension mapping can send an empty type
# entirely. Falling back to the file extension when the reported type is
# missing/generic/unrecognized avoids rejecting perfectly normal uploads.
SUBMISSION_EXTENSION_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _resolve_submission_mime_type(file_name: str, reported_mime_type: str | None) -> str | None:
    normalized = (reported_mime_type or "").split(";")[0].strip().lower()
    if normalized in ALLOWED_SUBMISSION_MIME_TYPES:
        return normalized
    return SUBMISSION_EXTENSION_MIME_TYPES.get(Path(file_name).suffix.lower())


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
    # Batched below (one query per collection, not per row) — the previous
    # per-member/per-task queries made a full class-sized group visibly
    # slow, and could look like the page had hung entirely.
    member_rows = groups_repo.list_members_with_students(db, group_id)
    members = [GroupMemberOut.from_row(m, s) for m, s in member_rows]

    task_rows = groups_repo.list_tasks(db, group_id)
    task_ids = [t.id for t in task_rows]
    submission_counts = groups_repo.count_submissions_by_task(db, task_ids)
    my_submissions = {} if is_owner else groups_repo.get_submissions_for_student(db, task_ids, user.id)

    tasks = [
        GroupTaskOut.from_row(
            task,
            submission_count=submission_counts.get(task.id, 0),
            my_submission=(
                TaskSubmissionOut.from_row(my_submissions[task.id], user) if task.id in my_submissions else None
            ),
        )
        for task in task_rows
    ]
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


def _get_group_task(db: Session, group_id: uuid.UUID, task_id: uuid.UUID) -> GroupTask:
    task = groups_repo.get_task_by_id(db, task_id)
    if task is None or task.group_id != group_id:
        raise AppError("TASK_NOT_FOUND", "Task not found.", 404)
    return task


def submit_task(
    db: Session,
    student: User,
    group_id: uuid.UUID,
    task_id: uuid.UUID,
    *,
    content: str,
    file_name: str | None,
    file_mime_type: str | None,
    file_data: bytes | None,
) -> GroupTaskSubmission:
    # Plain sync function run via run_in_threadpool from the router — the
    # route itself is async (it has to await UploadFile.read()), but this
    # function's DB calls are all blocking SQLAlchemy; running them directly
    # on the event loop would stall every other request on Render's
    # single-worker deployment for the duration of each DB round trip.
    #
    # A non-member (including the owning teacher, who is never a "member")
    # gets the same 404 as a nonexistent group — consistent with every
    # other member-only action in this module.
    if not _is_member(db, group_id, student.id):
        raise AppError("GROUP_NOT_FOUND", "Group not found.", 404)
    task = _get_group_task(db, group_id, task_id)

    file_size = None
    if file_data is not None:
        resolved_mime_type = _resolve_submission_mime_type(file_name or "", file_mime_type)
        if resolved_mime_type is None:
            raise AppError(
                "UNSUPPORTED_FILE_TYPE",
                "That file type isn't supported. Allowed: PDF, Word documents, text, and images.",
                400,
            )
        file_mime_type = resolved_mime_type
        if len(file_data) > MAX_UPLOAD_BYTES:
            raise AppError(
                "FILE_TOO_LARGE", f"Files must be under {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.", 400
            )
        if len(file_data) == 0:
            raise AppError("EMPTY_FILE", "The uploaded file is empty.", 400)
        file_size = len(file_data)
    else:
        file_name = None
        file_mime_type = None

    if not content.strip() and file_data is None:
        raise AppError("EMPTY_SUBMISSION", "Add some text or attach a file before submitting.", 400)

    return groups_repo.upsert_submission(
        db,
        task_id=task.id,
        student_id=student.id,
        content=content,
        file_name=file_name,
        file_mime_type=file_mime_type,
        file_size=file_size,
        file_data=file_data,
    )


def list_task_submissions(
    db: Session, teacher: User, group_id: uuid.UUID, task_id: uuid.UUID
) -> list[TaskSubmissionOut]:
    group = _get_owned_group(db, teacher, group_id)
    task = _get_group_task(db, group.id, task_id)
    rows = []
    for submission in groups_repo.list_submissions_for_task(db, task.id):
        student = users_repo.get_user_by_id(db, submission.student_id)
        if student is not None:
            rows.append(TaskSubmissionOut.from_row(submission, student))
    return rows


def get_submission_file(
    db: Session, user: User, group_id: uuid.UUID, task_id: uuid.UUID, submission_id: uuid.UUID
) -> GroupTaskSubmission:
    group = groups_repo.get_group_by_id(db, group_id)
    if group is None:
        raise AppError("GROUP_NOT_FOUND", "Group not found.", 404)
    task = _get_group_task(db, group.id, task_id)
    submission = groups_repo.get_submission_by_id(db, submission_id)
    if submission is None or submission.task_id != task.id:
        raise AppError("SUBMISSION_NOT_FOUND", "Submission not found.", 404)

    is_owner = group.teacher_id == user.id
    if not is_owner and submission.student_id != user.id:
        raise AppError("SUBMISSION_NOT_FOUND", "Submission not found.", 404)
    if submission.file_data is None:
        raise AppError("SUBMISSION_NOT_FOUND", "This submission has no attached file.", 404)
    return submission
