from sqlalchemy import Column, String, Integer, Float, ForeignKey
from backend.app.db.base import Base
import uuid

class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    from_account_id = Column(String, ForeignKey("accounts.id"), index=True, nullable=False)
    to_account_id = Column(String, ForeignKey("accounts.id"), index=True, nullable=False)
    edge_type = Column(String, nullable=False) # e.g., TRANSACTION, SHARED_DEVICE, SHARED_IP
    transaction_count = Column(Integer, default=1)
    total_amount = Column(Float, default=0.0)
