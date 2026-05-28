from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from backend.app.db.base import Base
import uuid

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), index=True, nullable=False)
    investigator_id = Column(String, index=True, nullable=True) # Could be a user ID
    status = Column(String, default="OPEN") # OPEN, IN_PROGRESS, RESOLVED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
