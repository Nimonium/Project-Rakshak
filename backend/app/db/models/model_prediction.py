from sqlalchemy import Column, String, Float, DateTime, func, ForeignKey, JSON
from backend.app.db.base import Base
import uuid

class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.id"), index=True, nullable=False)
    xgb_probability = Column(Float, nullable=False)
    isolation_score = Column(Float, nullable=False)
    graph_score = Column(Float, nullable=False)
    final_risk_score = Column(Float, nullable=False)
    
    # Store SHAP explanation as JSON
    shap_summary = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
