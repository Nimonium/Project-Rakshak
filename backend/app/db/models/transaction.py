from sqlalchemy import Column, String, Float, Boolean, DateTime, func, ForeignKey
from backend.app.db.base import Base
import uuid

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    sender_account_id = Column(String, ForeignKey("accounts.id"), index=True, nullable=False)
    receiver_account_id = Column(String, ForeignKey("accounts.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    ip_address = Column(String)
    device_id = Column(String)
    geo_location = Column(String)
    transaction_time = Column(DateTime(timezone=True), default=func.now(), index=True)
    ml_score = Column(Float)
    anomaly_flag = Column(Boolean, default=False)
