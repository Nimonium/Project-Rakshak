from sqlalchemy import Column, String, Float, Boolean, DateTime, func
from backend.app.db.base import Base
import uuid

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String, unique=True, index=True, nullable=False)
    customer_name = Column(String, nullable=False)
    risk_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    graph_score = Column(Float, default=0.0)
    is_frozen = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
