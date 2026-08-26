import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.pagination import PaginationParams, get_pagination_params
from app.modules.messaging import service as messaging_service
from app.modules.messaging.schemas import (
    ConversationOut,
    MessageableUserOut,
    MessageOut,
    ModerationConversationOut,
    SendMessageRequest,
    StartConversationRequest,
)
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/conversations", tags=["messaging"])


@router.get("")
def list_conversations(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    rows = messaging_service.list_my_conversations(db, current_user)
    data = [ConversationOut.from_row(*row).model_dump(mode="json") for row in rows]
    return success(data)


@router.post("", status_code=status.HTTP_201_CREATED)
def start_conversation(
    payload: StartConversationRequest, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> dict:
    row = messaging_service.start_conversation_row(db, current_user, payload.other_user_id)
    return success(ConversationOut.from_row(*row).model_dump(mode="json"))


@router.get("/messageable-users")
def list_messageable_users(
    current_user: CurrentUser, db: Annotated[Session, Depends(get_db)], search: str | None = None
) -> dict:
    users = messaging_service.list_messageable_users(db, current_user, search)
    data = [MessageableUserOut.model_validate(u).model_dump(mode="json") for u in users]
    return success(data)


@router.get("/moderation/all", dependencies=[Depends(require_permission("message:moderate"))])
def list_all_conversations_for_moderation(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
) -> dict:
    rows, total = messaging_service.list_all_conversations_for_moderation(
        db, pagination.offset, pagination.page_size
    )
    data = [ModerationConversationOut.from_row(*row).model_dump(mode="json") for row in rows]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.get("/{conversation_id}/messages")
def list_messages(
    conversation_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
) -> dict:
    rows, total = messaging_service.list_messages(
        db, current_user, conversation_id, pagination.offset, pagination.page_size
    )
    data = [MessageOut.from_row(message, sender).model_dump(mode="json") for message, sender in rows]
    return success(data, meta={"page": pagination.page, "page_size": pagination.page_size, "total": total})


@router.post("/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    message = messaging_service.send_message(db, current_user, conversation_id, payload.body)
    return success(MessageOut.from_row(message, current_user).model_dump(mode="json"))
