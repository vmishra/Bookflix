"""Chat endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import chat_service
from app.schemas.chat import ChatSessionCreate, ChatSessionOut, ChatMessageCreate, ChatMessageOut

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionOut)
async def create_session(
    request: ChatSessionCreate,
    db: AsyncSession = Depends(get_async_session),
):
    session = await chat_service.create_chat_session(
        db, title=request.title, book_ids=request.book_ids,
    )
    return ChatSessionOut.model_validate(session)


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session),
):
    sessions = await chat_service.get_chat_sessions(db, limit=limit)
    return [ChatSessionOut.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def get_messages(
    session_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    messages = await chat_service.get_chat_messages(db, session_id)
    return [ChatMessageOut.model_validate(m) for m in messages]


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageOut)
async def send_message(
    session_id: int,
    request: ChatMessageCreate,
    db: AsyncSession = Depends(get_async_session),
):
    message = await chat_service.send_message(db, session_id, request.content)
    return ChatMessageOut.model_validate(message)
