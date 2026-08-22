from fastapi import APIRouter

from app.dependencies.auth import CurrentUser
from app.modules.assistant import service as assistant_service
from app.modules.assistant.schemas import ChatRequest, ChatResponse
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])


@router.post("/chat")
def chat(payload: ChatRequest, current_user: CurrentUser) -> dict:
    reply, configured = assistant_service.chat(current_user, payload)
    data = ChatResponse(reply=reply, configured=configured).model_dump()
    return success(data)
