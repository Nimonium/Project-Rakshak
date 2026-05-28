from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from backend.app.schemas.transaction import TransactionResponse

class AccountBase(BaseModel):
    account_number: str
    customer_name: str

class AccountResponse(AccountBase):
    id: str
    risk_score: float
    anomaly_score: float
    graph_score: float
    is_frozen: bool
    created_at: datetime
    
    # Linked transactions could be included if joined
    transactions: Optional[List[TransactionResponse]] = None
    
    model_config = ConfigDict(from_attributes=True)
