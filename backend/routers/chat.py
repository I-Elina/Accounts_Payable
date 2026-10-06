from fastapi import APIRouter
from backend.schemas import ChatRequest, ChatResponse
from backend.services.chat_service import process_chat_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_assistant(chat_req: ChatRequest) -> ChatResponse:
    return process_chat_message(chat_req=chat_req)
