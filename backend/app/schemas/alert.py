from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AlertBase(BaseModel):
    transaction_id: Optional[str] = None
    account_id: Optional[str] = None
    severity: str
    alert_type: str
    confidence: float
    status: str

class AlertResponse(AlertBase):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
