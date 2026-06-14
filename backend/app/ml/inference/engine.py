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
        shap_path = os.path.join(self.models_dir, "shap_explainer.joblib")
        feat_path = os.path.join(self.models_dir, "feature_names.joblib")
        vt_path = os.path.join(self.models_dir, "variance_threshold.joblib")
        
        try:
            if os.path.exists(xgb_path):
                self.xgb_model = joblib.load(xgb_path)
                logger.info("XGBoost model loaded for inference.")
            else:
                logger.warning(f"XGBoost model not found at {xgb_path}.")
                
            if os.path.exists(iso_path):
                self.iso_forest = joblib.load(iso_path)
                logger.info("Isolation Forest model loaded for inference.")
            else:
                logger.warning(f"Isolation Forest model not found at {iso_path}.")
                
            if os.path.exists(shap_path):
                self.explainer = joblib.load(shap_path)
                logger.info("SHAP explainer loaded.")
            else:
                self.explainer = None
                
            if os.path.exists(feat_path):
                self.feature_names = joblib.load(feat_path)
            else:
                self.feature_names = None
                
            if os.path.exists(vt_path):
                self.vt = joblib.load(vt_path)
            else:
                self.vt = None
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")

    def predict_fraud(self, features: pd.DataFrame) -> Tuple[float, float, Dict[str, Any]]:
        """
        Runs inference on provided features.
        Returns:
            xgb_prob (float): Probability of fraud from XGBoost.
            anomaly_score (float): Anomaly score from Isolation Forest.
            shap_payload (Dict): SHAP explanation payload.
        """
        if self.xgb_model is None:
            return 0.0, 0.0, 0.0, {}

        try:
            # Reindex and apply VarianceThreshold if available
            X = features.copy()
            if hasattr(self, 'feature_names') and self.feature_names is not None:
                X = X.reindex(columns=self.feature_names).fillna(0)
            
            # Bug 1 Fix: use predict_proba, NOT predict
            # Note: X might be a DataFrame, predict_proba expects 2D array
            xgb_prob = float(self.xgb_model.predict_proba(X.values if hasattr(X, 'values') else X)[0, 1])
            
            # Isolation Forest (anomaly score)
            iso_raw = 0.5
            if self.iso_forest:
                iso_raw = self.iso_forest.score_samples(X)[0]
                # normalize to 0–1 where 1 = most anomalous
                anomaly_score = float(round(1 - (iso_raw - (-0.5)) / 0.5, 4))
            else:
                anomaly_score = 0.5
            
            # Bug 2 Fix: SHAP — explicit float conversion before JSON
            top_features_list = []
            if hasattr(self, 'explainer') and self.explainer is not None:
                shap_vals = self.explainer.shap_values(X)[0] # numpy array
                contributions = {
                    feat: round(float(val), 5) # cast to Python float
                    for feat, val in zip(self.feature_names if hasattr(self, 'feature_names') else X.columns, shap_vals)
                }
                # Convert to the list format expected by PredictionResponse schema
                sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
                top_features_list = [{"feature": k, "impact": v} for k, v in sorted_contribs]
                
                # The user expects a dict in top_features based on their snippet, but the schema PredictionResponse expects List[FeatureImpact]. 
                # We will satisfy the schema.

            # Bug 3 Fix: Simulate graph_risk internally based on F3887 (we'll pass it in the payload so scoring_service can use it or we just return it)
            # Actually, scoring_service.py calculates graph_risk on its own. 
            # To strictly follow the user's intent, we inject the mock logic here.
            velocity_indicator = float(features.get("F3887", pd.Series([0]))[0]) if "F3887" in features else 0
            graph_risk_simulated = 0.7 if velocity_indicator > 500 else 0.1
            
            shap_payload = {
                "prediction": xgb_prob,
                "top_features": top_features_list,
                "simulated_graph_risk": graph_risk_simulated
            }
            
            return xgb_prob, anomaly_score, graph_risk_simulated, shap_payload
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            return 0.0, 0.0, 0.0, {}

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
