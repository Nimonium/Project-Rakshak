from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TransactionBase(BaseModel):
    sender_account_id: str
    receiver_account_id: str
    amount: float
    transaction_type: str
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    geo_location: Optional[str] = None

class TransactionCreate(TransactionBase):
    # This might have extra raw features in real life
    pass

class TransactionResponse(TransactionBase):
    id: str
    transaction_time: datetime
    ml_score: Optional[float] = None
    anomaly_flag: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)
