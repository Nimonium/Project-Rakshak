from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class FeatureImpact(BaseModel):
    feature: str
    impact: float

class PredictionResponse(BaseModel):
    fraud_probability: float
    anomaly_score: float
    graph_risk: float
    final_risk_score: float
    top_features: List[FeatureImpact]
    
    # Store full SHAP explanation if needed
    shap_summary: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)
