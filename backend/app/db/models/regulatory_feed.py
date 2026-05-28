from sqlalchemy import Column, String, Float, DateTime, func
from backend.app.db.base import Base
import uuid

class RegulatoryFeed(Base):
    __tablename__ = "regulatory_feeds"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False, index=True) # e.g., RBI, CERT-In
    entity_type = Column(String, nullable=False) # IP, DEVICE, ACCOUNT, NAME
    entity_value = Column(String, nullable=False, index=True)
    risk_weight = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
