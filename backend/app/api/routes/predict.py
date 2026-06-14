from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api import deps
from backend.app.schemas.transaction import TransactionCreate
from backend.app.schemas.prediction import PredictionResponse
from backend.app.services.transaction_service import transaction_service
from backend.app.core.websocket_manager import manager
from typing import Any, List

router = APIRouter()

async def async_broadcast(db_tx: Any, scoring_results: dict):
    # Retrieve alert if we created one? In this simple flow we won't pass alert to broadcast directly,
    # or we can refactor later. For now, broadcast tx + score.
    await manager.broadcast_transaction(db_tx, scoring_results)

@router.post("/", response_model=PredictionResponse)
async def predict_fraud(
    tx_in: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Ingests a transaction, scores it, generates alerts, and returns the risk explanation.
    """
    db_tx, scoring_results = await transaction_service.process_transaction(tx_in, db)
    
    # Broadcast in background
    background_tasks.add_task(async_broadcast, db_tx, scoring_results)
    
    return PredictionResponse(
        fraud_probability=scoring_results.get("xgb_probability", 0.0),
        anomaly_score=scoring_results.get("anomaly_score", 0.0),
        graph_risk=scoring_results.get("graph_risk", 0.0),
        final_risk_score=scoring_results.get("final_risk_score", 0.0),
        top_features=scoring_results.get("shap_explanation", {}).get("top_features", []),
        shap_summary=scoring_results.get("shap_explanation", {})
    )

@router.post("/batch", response_model=List[PredictionResponse])
async def predict_fraud_batch(
    tx_in_list: List[TransactionCreate],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Ingests a batch of transactions for high throughput processing.
    """
    responses = []
    # For a true production system, we'd batch the DB inserts and ML inference natively.
    # For now, we iterate async to reuse the robust scoring pipeline.
    for tx_in in tx_in_list:
        db_tx, scoring_results = await transaction_service.process_transaction(tx_in, db)
        background_tasks.add_task(async_broadcast, db_tx, scoring_results)
        
        responses.append(
            PredictionResponse(
                fraud_probability=scoring_results.get("xgb_probability", 0.0),
                anomaly_score=scoring_results.get("anomaly_score", 0.0),
                graph_risk=scoring_results.get("graph_risk", 0.0),
                final_risk_score=scoring_results.get("final_risk_score", 0.0),
                top_features=scoring_results.get("shap_explanation", {}).get("top_features", []),
                shap_summary=scoring_results.get("shap_explanation", {})
            )
        )
    return responses
