from sqlalchemy import Column, String, Float, DateTime, func, ForeignKey
from backend.app.db.base import Base
import uuid

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.id"), index=True, nullable=True)
    account_id = Column(String, ForeignKey("accounts.id"), index=True, nullable=True)
    severity = Column(String, nullable=False) # low, medium, high, critical
    alert_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String, default="NEW") # NEW, INVESTIGATING, CLOSED_TRUE_POSITIVE, CLOSED_FALSE_POSITIVE
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
