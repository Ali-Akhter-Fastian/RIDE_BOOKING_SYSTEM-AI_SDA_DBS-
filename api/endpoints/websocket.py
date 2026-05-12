from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.ws import ws_hub

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/rider/{user_id}")
async def rider_ws(websocket: WebSocket, user_id: UUID) -> None:
    await ws_hub.connect_rider(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_hub.disconnect_rider(user_id, websocket)
    except Exception:
        ws_hub.disconnect_rider(user_id, websocket)


@router.websocket("/ws/driver/{driver_id}")
async def driver_ws(websocket: WebSocket, driver_id: UUID) -> None:
    await ws_hub.connect_driver(driver_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_hub.disconnect_driver(driver_id, websocket)
    except Exception:
        ws_hub.disconnect_driver(driver_id, websocket)
