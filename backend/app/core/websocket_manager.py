import structlog
from typing import List, Dict, Any
from fastapi import WebSocket

logger = structlog.get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON message to all connected clients."""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                disconnected_clients.append(connection)
                
        # Clean up dead connections
        for client in disconnected_clients:
            self.disconnect(client)

    async def broadcast_transaction(self, db_tx: Any, scoring_results: Dict[str, Any], alert: Any = None):
        """Helper to format and broadcast a transaction event."""
        payload = {
            "type": "NEW_TRANSACTION",
            "data": {
                "transaction_id": db_tx.id,
                "sender": db_tx.sender_account_id,
                "receiver": db_tx.receiver_account_id,
                "amount": db_tx.amount,
                "transaction_type": db_tx.transaction_type,
                "final_risk_score": db_tx.ml_score,
                "is_anomalous": db_tx.anomaly_flag
            },
            "scores": scoring_results,
            "alert": None
        }
        
        if alert:
            payload["alert"] = {
                "alert_id": alert.id,
                "severity": alert.severity,
                "type": alert.alert_type
            }
            
        await self.broadcast(payload)

manager = ConnectionManager()
