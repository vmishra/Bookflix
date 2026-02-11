"""RAG chat pipeline."""
import logging
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatSession, ChatMessage
from app.services.search_service import hybrid_search
from app.llm.client import llm_client
from app.llm.prompts import CHAT_SYSTEM, CHAT_WITH_CONTEXT

logger = logging.getLogger(__name__)


async def create_chat_session(
    db: AsyncSession,
    title: str = "New Chat",
    book_ids: list[int] | None = None,
) -> ChatSession:
    session = ChatSession(title=title, book_ids=book_ids or [])
    db.add(session)
    await db.flush()
    return session


async def get_chat_sessions(db: AsyncSession, limit: int = 20) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.is_active.is_(True))
        .order_by(desc(ChatSession.updated_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_chat_messages(db: AsyncSession, session_id: int) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())


async def send_message(
    db: AsyncSession,
    session_id: int,
    user_message: str,
) -> ChatMessage:
    session = await db.get(ChatSession, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=user_message,
    )
    db.add(user_msg)
    await db.flush()

    # RAG: retrieve relevant chunks
    book_ids = session.book_ids if session.book_ids else None
    search_results = await hybrid_search(db, user_message, limit=8, book_ids=book_ids)

    context_parts = []
    source_chunks = []
    for r in search_results:
        context_parts.append(
            f"[{r.get('book_title', 'Unknown')} - p.{r.get('page_number', '?')}]\n{r['content']}"
        )
        source_chunks.append({
            "chunk_id": r["chunk_id"],
            "book_title": r.get("book_title"),
            "page_number": r.get("page_number"),
            "snippet": r["content"][:200],
        })

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant content found."

    # Build conversation history
    history = await get_chat_messages(db, session_id)
    messages = [{"role": "system", "content": CHAT_SYSTEM}]
    for msg in history[-10:]:  # Last 10 messages for context
        if msg.id == user_msg.id:
            continue
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({
        "role": "user",
        "content": CHAT_WITH_CONTEXT.format(context=context, question=user_message),
    })

    response = await llm_client.complete(messages=messages, task_type="chat")

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=response,
        source_chunks=source_chunks,
        model_used=llm_client.registry.get_model("chat"),
    )
    db.add(assistant_msg)
    await db.flush()

    return assistant_msg


async def stream_message(db: AsyncSession, session_id: int, user_message: str):
    """Stream a chat response. Yields content chunks."""
    session = await db.get(ChatSession, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    user_msg = ChatMessage(session_id=session_id, role="user", content=user_message)
    db.add(user_msg)
    await db.flush()

    book_ids = session.book_ids if session.book_ids else None
    search_results = await hybrid_search(db, user_message, limit=8, book_ids=book_ids)

    context_parts = []
    source_chunks = []
    for r in search_results:
        context_parts.append(f"[{r.get('book_title', 'Unknown')} - p.{r.get('page_number', '?')}]\n{r['content']}")
        source_chunks.append({
            "chunk_id": r["chunk_id"],
            "book_title": r.get("book_title"),
            "page_number": r.get("page_number"),
            "snippet": r["content"][:200],
        })

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant content found."

    messages = [
        {"role": "system", "content": CHAT_SYSTEM},
        {"role": "user", "content": CHAT_WITH_CONTEXT.format(context=context, question=user_message)},
    ]

    full_response = ""
    async for chunk in llm_client.complete_stream(messages=messages, task_type="chat"):
        full_response += chunk
        yield {"type": "content", "data": chunk}

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=full_response,
        source_chunks=source_chunks,
        model_used=llm_client.registry.get_model("chat"),
    )
    db.add(assistant_msg)
    await db.flush()

    yield {"type": "sources", "data": source_chunks}
    yield {"type": "done", "data": {"message_id": assistant_msg.id}}
