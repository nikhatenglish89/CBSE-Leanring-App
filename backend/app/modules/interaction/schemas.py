import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QuestionCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class AnswerUpsertRequest(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class AnswerOut(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    teacher_id: uuid.UUID
    teacher_name: str
    body: str
    created_at: datetime

    @classmethod
    def from_row(cls, answer, teacher) -> "AnswerOut":
        return cls(
            id=answer.id,
            question_id=answer.question_id,
            teacher_id=answer.teacher_id,
            teacher_name=teacher.full_name,
            body=answer.body,
            created_at=answer.created_at,
        )


class QuestionOut(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    body: str
    created_at: datetime
    answer: AnswerOut | None = None

    @classmethod
    def from_row(cls, question, student, answer, answerer) -> "QuestionOut":
        return cls(
            id=question.id,
            lesson_id=question.lesson_id,
            student_id=question.student_id,
            student_name=student.full_name,
            body=question.body,
            created_at=question.created_at,
            answer=AnswerOut.from_row(answer, answerer) if answer is not None else None,
        )


class QuestionBrowseOut(QuestionOut):
    """A question plus enough context to show and link to it from the
    platform-wide Teacher Interaction hub."""

    lesson_title: str
    course_id: uuid.UUID
    course_title: str
    course_status: str
    class_id: uuid.UUID
    class_name: str
    subject_id: uuid.UUID
    subject_name: str

    @classmethod
    def from_row(  # type: ignore[override]
        cls, question, student, answer, answerer, lesson, course, klass, subject
    ) -> "QuestionBrowseOut":
        base = QuestionOut.from_row(question, student, answer, answerer)
        return cls(
            **base.model_dump(),
            lesson_title=lesson.title,
            course_id=course.id,
            course_title=course.title,
            course_status=course.status,
            class_id=klass.id,
            class_name=klass.name,
            subject_id=subject.id,
            subject_name=subject.name,
        )


class LiveClassCreateRequest(BaseModel):
    class_id: uuid.UUID
    subject_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    scheduled_at: datetime
    meeting_url: str = Field(min_length=1, max_length=1000)


class LiveClassUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    scheduled_at: datetime | None = None
    meeting_url: str | None = Field(default=None, min_length=1, max_length=1000)


class LiveClassOut(BaseModel):
    id: uuid.UUID
    class_id: uuid.UUID
    class_name: str
    subject_id: uuid.UUID
    subject_name: str
    teacher_id: uuid.UUID
    teacher_name: str
    title: str
    description: str
    scheduled_at: datetime
    meeting_url: str
    created_at: datetime

    @classmethod
    def from_row(cls, live_class, klass, subject, teacher) -> "LiveClassOut":
        return cls(
            id=live_class.id,
            class_id=klass.id,
            class_name=klass.name,
            subject_id=subject.id,
            subject_name=subject.name,
            teacher_id=live_class.teacher_id,
            teacher_name=teacher.full_name,
            title=live_class.title,
            description=live_class.description,
            scheduled_at=live_class.scheduled_at,
            meeting_url=live_class.meeting_url,
            created_at=live_class.created_at,
        )
