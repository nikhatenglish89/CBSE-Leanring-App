import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationParticipantOut(BaseModel):
    id: uuid.UUID
    full_name: str
    role: str


class ConversationOut(BaseModel):
    id: uuid.UUID
    other_user: ConversationParticipantOut
    last_message_preview: str | None
    last_message_at: datetime | None
    unread_count: int

    @classmethod
    def from_row(cls, conversation, other_user, last_message, unread_count: int) -> "ConversationOut":
        return cls(
            id=conversation.id,
            other_user=ConversationParticipantOut(
                id=other_user.id, full_name=other_user.full_name, role=other_user.role.name
            ),
            last_message_preview=(last_message.body[:140] if last_message else None),
            last_message_at=last_message.created_at if last_message else None,
            unread_count=unread_count,
        )


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    sender_name: str
    body: str
    created_at: datetime
    read_at: datetime | None

    @classmethod
    def from_row(cls, message, sender) -> "MessageOut":
        return cls(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            sender_name=sender.full_name,
            body=message.body,
            created_at=message.created_at,
            read_at=message.read_at,
        )


class StartConversationRequest(BaseModel):
    other_user_id: uuid.UUID


class SendMessageRequest(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class MessageableUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str


class ModerationConversationOut(BaseModel):
    id: uuid.UUID
    student_name: str
    teacher_name: str
    last_message_preview: str | None
    last_message_at: datetime | None
    message_count: int

    @classmethod
    def from_row(cls, conversation, student, teacher, last_message, message_count: int) -> "ModerationConversationOut":
        return cls(
            id=conversation.id,
            student_name=student.full_name,
            teacher_name=teacher.full_name,
            last_message_preview=(last_message.body[:140] if last_message else None),
            last_message_at=last_message.created_at if last_message else None,
            message_count=message_count,
        )
