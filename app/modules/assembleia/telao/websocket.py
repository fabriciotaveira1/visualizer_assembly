from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.assembleia.telao.manager import telao_manager
from app.modules.assembleia.telao.service import validar_assembleia


router = APIRouter()


@router.websocket("/ws/telao/{assembleia_id}")
async def telao_websocket(
    websocket: WebSocket,
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    try:
        validar_assembleia(db, assembleia_id)
    except Exception:  # noqa: BLE001
        await websocket.close(code=1008)
        return

    await telao_manager.connect(assembleia_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if message.strip().lower() == "ping":
                await websocket.send_json({"evento": "pong", "data": {"assembleia_id": str(assembleia_id)}})
    except WebSocketDisconnect:
        await telao_manager.disconnect(assembleia_id, websocket)
    except Exception:  # noqa: BLE001
        await telao_manager.disconnect(assembleia_id, websocket)


