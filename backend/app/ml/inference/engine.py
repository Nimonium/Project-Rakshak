import os
import joblib
import pandas as pd
import numpy as np
import structlog
from typing import Dict, Any, Tuple
from backend.app.ml.explainability.shap_engine import ShapEngine

logger = structlog.get_logger(__name__)

class InferenceEngine:
    def __init__(self, models_dir: str = "artifacts/models"):
        self.models_dir = models_dir
        self.xgb_model = None
        self.iso_forest = None
        self.shap_engine = None
        self._load_models()

    def _load_models(self):
        xgb_path = os.path.join(self.models_dir, "xgboost_model.joblib")
        iso_path = os.path.join(self.models_dir, "isolation_forest.joblib")
        
        try:
            if os.path.exists(xgb_path):
                self.xgb_model = joblib.load(xgb_path)
                logger.info("XGBoost model loaded for inference.")
                self.shap_engine = ShapEngine(xgb_path)
            else:
                logger.warning(f"XGBoost model not found at {xgb_path}.")
                
            if os.path.exists(iso_path):
                self.iso_forest = joblib.load(iso_path)
                logger.info("Isolation Forest model loaded for inference.")
            else:
                logger.warning(f"Isolation Forest model not found at {iso_path}.")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")

    def predict_fraud(self, features: pd.DataFrame) -> Tuple[float, float, Dict[str, Any]]:
        """
        Runs inference on provided features.
        Returns:
            xgb_prob (float): Probability of fraud from XGBoost.
            anomaly_score (float): Anomaly score from Isolation Forest (normalized 0-1).
            shap_payload (Dict): SHAP explanation payload.
        """
        if self.xgb_model is None or self.iso_forest is None:
            logger.error("Models are not loaded. Cannot run inference.")
            return 0.0, 0.0, {}

        try:
            # 1. XGBoost Probability
            xgb_prob = float(self.xgb_model.predict_proba(features)[0, 1])
            
            # 2. Isolation Forest Score
            # decision_function returns negative values for anomalies, positive for normal
            # Let's normalize it to a 0-1 risk score where 1 is highly anomalous
            iso_raw = float(self.iso_forest.decision_function(features)[0])
            # Sigmoid-like transformation for anomaly score (heuristic)
            anomaly_score = 1.0 / (1.0 + np.exp(iso_raw * 2))
            
            # 3. SHAP Explainability
            shap_payload = self.shap_engine.explain_prediction(features, xgb_prob) if self.shap_engine else {}
            
            return xgb_prob, anomaly_score, shap_payload
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            return 0.0, 0.0, {}

    def predict_batch(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs batched inference for high throughput.
        """
        if self.xgb_model is None or self.iso_forest is None:
            return pd.DataFrame()
            
        xgb_probs = self.xgb_model.predict_proba(features_df)[:, 1]
        iso_raws = self.iso_forest.decision_function(features_df)
        anomaly_scores = 1.0 / (1.0 + np.exp(iso_raws * 2))
        
        results = pd.DataFrame({
            'xgb_probability': xgb_probs,
            'anomaly_score': anomaly_scores
        })
        return results

# Singleton instance for the app
inference_engine = InferenceEngine()
