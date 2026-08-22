from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    # Prior turns, oldest first — kept client-side (no server-side chat
    # storage for v1) and capped so a long-running conversation can't blow
    # up the request payload or the LLM's context.
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str
    # False when no LLM_API_KEY is configured — reply is a canned fallback
    # message rather than a real model response. Lets the frontend show a
    # subtle "not fully set up" hint instead of pretending it's AI.
    configured: bool
