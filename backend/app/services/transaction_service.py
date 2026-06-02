import structlog
import uuid
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.schemas.transaction import TransactionCreate
from backend.app.db.models.transaction import Transaction
from backend.app.db.models.model_prediction import ModelPrediction
from backend.app.db.models.account import Account
from backend.app.services.scoring_service import scoring_service
from backend.app.services.alert_service import alert_service
# from backend.app.core.websocket_manager import manager # We will import this later

logger = structlog.get_logger(__name__)

class TransactionService:
    async def _ensure_account_exists(self, account_id: str, session: AsyncSession):
        """Auto-create account if it doesn't exist (development convenience)."""
        result = await session.execute(select(Account).where(Account.id == account_id))
        if not result.scalars().first():
            account = Account(
                id=account_id,
                account_number=account_id,
                customer_name=f"Auto-created {account_id}",
            )
            session.add(account)
            await session.flush()

    async def process_transaction(self, tx_in: TransactionCreate, session: AsyncSession) -> Tuple[Transaction, Dict[str, Any]]:
        """
        Process a new transaction: Score it, Save it, Alert on it, Broadcast it.
        """
        tx_id = str(uuid.uuid4())
        
        # 1. Score the transaction
        final_score, scoring_results = await scoring_service.score_transaction(tx_in)
        
        # 2. Ensure sender and receiver accounts exist
        await self._ensure_account_exists(tx_in.sender_account_id, session)
        await self._ensure_account_exists(tx_in.receiver_account_id, session)
        
        # 3. Save transaction to DB
        db_tx = Transaction(
            id=tx_id,
            sender_account_id=tx_in.sender_account_id,
            receiver_account_id=tx_in.receiver_account_id,
            amount=tx_in.amount,
            transaction_type=tx_in.transaction_type,
            ip_address=tx_in.ip_address,
            device_id=tx_in.device_id,
            geo_location=tx_in.geo_location,
            ml_score=final_score,
            anomaly_flag=final_score > 0.7
        )
        session.add(db_tx)
        
        # Flush transaction first so FK-dependent records can reference it
        await session.flush()
        
        # 3. Save prediction results
        db_pred = ModelPrediction(
            transaction_id=tx_id,
            xgb_probability=scoring_results.get("xgb_probability", 0.0),
            isolation_score=scoring_results.get("anomaly_score", 0.0),
            graph_score=scoring_results.get("graph_risk", 0.0),
            final_risk_score=final_score,
            shap_summary=scoring_results.get("shap_explanation", {})
        )
        session.add(db_pred)
        
        # 4. Generate Alerts
        alert = alert_service.evaluate_and_create_alert(tx_in, tx_id, scoring_results, session)
        if alert:
            session.add(alert)
            
        await session.commit()
        await session.refresh(db_tx)
        
        # 5. Broadcast via WebSocket (Handled in the router/worker, but could be here)
        # await manager.broadcast_transaction(db_tx, scoring_results, alert)
        
        return db_tx, scoring_results

transaction_service = TransactionService()
