from __future__ import annotations

import asyncio
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class TelaoConnectionManager:
    """In-memory WebSocket manager.

    The storage strategy is intentionally simple so we can swap it for Redis/pubsub later.
    """

    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, assembleia_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[assembleia_id].add(websocket)

    async def disconnect(self, assembleia_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(assembleia_id)
            if connections is None:
                return
            connections.discard(websocket)
            if not connections:
                self._connections.pop(assembleia_id, None)

    async def broadcast(self, assembleia_id: UUID, message: dict) -> None:
        async with self._lock:
            connections = list(self._connections.get(assembleia_id, set()))

        stale_connections: list[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:  # noqa: BLE001
                stale_connections.append(connection)

        for connection in stale_connections:
            await self.disconnect(assembleia_id, connection)


telao_manager = TelaoConnectionManager()


