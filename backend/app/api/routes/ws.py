from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.core.websocket_manager import manager
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.websocket("/transactions")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client in this flow,
            # but we need to receive to keep the connection alive and catch disconnects.
            data = await websocket.receive_text()
            logger.info(f"Received message from WS client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket.")
