"""WebSocket endpoints."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.ws_manager import ws_manager
from app.db.session import async_session_factory
from app.services import chat_service
import json
import logging

logger = logging.getLogger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/processing")
async def ws_processing(websocket: WebSocket):
    """WebSocket for processing progress updates."""
    await ws_manager.connect(websocket, "processing")
    try:
        while True:
            data = await websocket.receive_text()
            # Client can send ping/subscribe messages
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "processing")


@ws_router.websocket("/ws/chat/{session_id}")
async def ws_chat(websocket: WebSocket, session_id: int):
    """WebSocket for streaming chat responses."""
    await ws_manager.connect(websocket, f"chat_{session_id}")
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                user_content = msg.get("content", "")

                async with async_session_factory() as db:
                    try:
                        async for chunk in chat_service.stream_message(db, session_id, user_content):
                            await websocket.send_json(chunk)
                        await db.commit()
                    except Exception as e:
                        await db.rollback()
                        await websocket.send_json({"type": "error", "data": str(e)})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, f"chat_{session_id}")
