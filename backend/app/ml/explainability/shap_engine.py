import os
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import structlog
from typing import Dict, Any, List

logger = structlog.get_logger(__name__)

class ShapEngine:
    def __init__(self, model_path: str = "artifacts/models/xgboost_model.joblib", export_dir: str = "artifacts/shap"):
        self.model_path = model_path
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.model = None
        self.explainer = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                # TreeExplainer is fast for XGBoost
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("SHAP explainer initialized successfully.")
            else:
                logger.warning(f"Model not found at {self.model_path}. SHAP Engine requires a trained model.")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP Engine: {str(e)}")

    def explain_prediction(self, features: pd.DataFrame, prediction_prob: float) -> Dict[str, Any]:
        """
        Generate local explanation for a single prediction.
        Returns a JSON-serializable dictionary with top features.
        """
        if self.explainer is None:
            return {"prediction": prediction_prob, "top_features": []}

        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # For a single instance
            if len(shap_values.shape) > 1 and shap_values.shape[0] == 1:
                instance_shap = shap_values[0]
            else:
                instance_shap = shap_values
                
            # 1. Generate plot exports for the first few features (or summary if batch)
            try:
                # Summary Plot (if we passed a batch, but we usually pass one instance here)
                # Waterfall plot for single instance
                plt.figure()
                shap.waterfall_plot(shap.Explanation(values=instance_shap, 
                                                     base_values=self.explainer.expected_value, 
                                                     data=features.iloc[0], 
                                                     feature_names=features.columns), show=False)
                plt.savefig(os.path.join(self.export_dir, "waterfall_plot.png"), bbox_inches='tight')
                plt.close()
            except Exception as plot_e:
                logger.warning(f"Could not generate SHAP plots: {plot_e}")
                plt.close()
            
            # Combine feature names and their impact
            feature_impacts = []
            risk_factors = []
            for idx, col in enumerate(features.columns):
                impact = float(instance_shap[idx])
                if abs(impact) > 0.01: # Filter out near-zero impacts
                    feature_impacts.append({
                        "feature": col,
                        "impact": round(impact, 4)
                    })
                    if impact > 0.1: # Significant positive impact towards fraud
                        risk_factors.append(f"High {col} increases risk")
                    
            # Sort by absolute impact descending
            feature_impacts = sorted(feature_impacts, key=lambda x: abs(x["impact"]), reverse=True)
            top_features = feature_impacts[:5]

            action = "freeze_account" if prediction_prob > 0.85 else ("investigate" if prediction_prob > 0.6 else "allow")

            return {
                "prediction": round(prediction_prob, 4),
                "confidence": round(abs(prediction_prob - 0.5) * 2, 4), # Confidence metric
                "top_features": top_features,
                "risk_factors": risk_factors[:3],
                "recommended_action": action
            }
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {str(e)}")
            return {"prediction": prediction_prob, "confidence": 0.0, "top_features": [], "risk_factors": [], "recommended_action": "allow"}
