import structlog
import pandas as pd
from typing import Dict, Any, Tuple
from backend.app.schemas.transaction import TransactionCreate, TransactionResponse
from backend.app.ml.inference.engine import inference_engine
from backend.app.ml.graph.graph_risk import GraphRiskEngine
from backend.app.ml.graph.graph_builder import GraphBuilder
from backend.app.services.rule_engine import rule_engine
# We will inject services and websocket manager as needed

logger = structlog.get_logger(__name__)

class ScoringService:
    def __init__(self, graph_builder: GraphBuilder):
        self.graph_builder = graph_builder
        self.graph_risk_engine = GraphRiskEngine(self.graph_builder.get_graph())
        
    def _extract_features(self, tx: TransactionCreate) -> pd.DataFrame:
        """
        Mock feature extraction.
        In a real system, this would fetch historical features from a Feature Store (Redis)
        and append the current transaction details, then run through the pipeline.
        """
        # Create a dummy dataframe with the required columns for inference
        # Assuming inference engine expects 18 high signal features + temporal/velocity
        # This is a placeholder for the actual feature vector construction
        feature_dict = {f"F{i}": [0.0] for i in range(50)} 
        feature_dict['amount'] = [tx.amount]
        return pd.DataFrame(feature_dict)

    def _build_historical_context(self, tx: TransactionCreate) -> Dict[str, Any]:
        """Mocks fetching historical context from Redis for the rule engine."""
        return {
            "velocity_5m": 2, # Example mock data
            "failed_24h": 0,
            "days_since_last_tx": 5,
            "fan_out_24h": 1,
            "geo_shift_flag": False,
            "cash_out_ratio": 0.1
        }



    async def score_transaction(self, tx: TransactionCreate) -> Tuple[float, Dict[str, Any]]:
        """
        Runs the full scoring pipeline.
        Returns final_score and explanation payload.
        """
        logger.info(f"Scoring transaction {tx.sender_account_id} -> {tx.receiver_account_id} (${tx.amount})")
        
        # 1. Feature Engineering (Construct feature vector)
        features_df = self._extract_features(tx)
        
        # 2. ML Inference (XGBoost + Isolation Forest + SHAP)
        xgb_prob, anomaly_score, graph_risk, shap_payload = inference_engine.predict_fraud(features_df)
        
        # 3. Graph Risk
        # Add to graph first (for real-time updates)
        self.graph_builder.add_transaction(
            tx.sender_account_id, 
            tx.receiver_account_id, 
            tx.amount, 
            "temp_tx_id"
        )
        # graph_risk is now computed once by engine.py as requested.
        
        # 4. Rules Engine
        historical_context = self._build_historical_context(tx)
        rule_score = rule_engine.evaluate(tx, historical_context)
        
        # 5. Ensemble Risk Score
        final_score = (
            0.4 * xgb_prob +
            0.3 * anomaly_score +
            0.2 * graph_risk +
            0.1 * rule_score
        )
        
        result_payload = {
            "xgb_probability": xgb_prob,
            "anomaly_score": anomaly_score,
            "graph_risk": graph_risk,
            "rule_score": rule_score,
            "final_risk_score": final_score,
            "shap_explanation": shap_payload
        }
        
        logger.info(f"Final Risk Score: {final_score:.4f}")
        return final_score, result_payload

# Create a singleton graph builder and scoring service for the app
# In production, GraphBuilder state should be managed via Redis/Graph DB.
global_graph_builder = GraphBuilder()
scoring_service = ScoringService(global_graph_builder)
