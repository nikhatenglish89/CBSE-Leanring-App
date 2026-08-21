import uuid

from pydantic import BaseModel, ConfigDict, Field


class PracticeSetSummaryOut(BaseModel):
    """Listing view — no questions, just enough to browse and pick a set."""

    id: uuid.UUID
    class_id: uuid.UUID
    class_name: str
    subject_id: uuid.UUID
    subject_name: str
    title: str
    question_count: int

    @classmethod
    def from_row(cls, practice_set, klass, subject, question_count: int) -> "PracticeSetSummaryOut":
        return cls(
            id=practice_set.id,
            class_id=klass.id,
            class_name=klass.name,
            subject_id=subject.id,
            subject_name=subject.name,
            title=practice_set.title,
            question_count=question_count,
        )


class PracticeQuestionOut(BaseModel):
    """What a learner sees while taking the test — correct_index withheld."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_text: str
    options: list[str]
    display_order: int


class PracticeSetDetailOut(BaseModel):
    id: uuid.UUID
    class_id: uuid.UUID
    class_name: str
    subject_id: uuid.UUID
    subject_name: str
    title: str
    questions: list[PracticeQuestionOut]


class PracticeAnswer(BaseModel):
    question_id: uuid.UUID
    selected_index: int = Field(ge=0, le=3)


class PracticeSubmitRequest(BaseModel):
    answers: list[PracticeAnswer]


class PracticeQuestionResult(BaseModel):
    question_id: uuid.UUID
    question_text: str
    options: list[str]
    correct_index: int
    selected_index: int | None
    is_correct: bool
    explanation: str


class PracticeSubmitResult(BaseModel):
    score: int
    total: int
    results: list[PracticeQuestionResult]
