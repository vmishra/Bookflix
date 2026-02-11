"""WebSocket connection manager."""
import logging
import json
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "default"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")

    def disconnect(self, websocket: WebSocket, channel: str = "default"):
        if channel in self.active_connections:
            self.active_connections[channel] = [
                ws for ws in self.active_connections[channel] if ws != websocket
            ]
            logger.info(f"WebSocket disconnected from channel: {channel}")

    async def send_json(self, data: dict, channel: str = "default"):
        if channel not in self.active_connections:
            return
        disconnected = []
        for ws in self.active_connections[channel]:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws, channel)

    async def broadcast(self, data: dict):
        for channel in list(self.active_connections.keys()):
            await self.send_json(data, channel)


ws_manager = ConnectionManager()
