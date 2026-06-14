from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class InvestigationBase(BaseModel):
    alert_id: str
    investigator_id: Optional[str] = None
    status: Optional[str] = "OPEN"
    notes: Optional[str] = None

class InvestigationCreate(InvestigationBase):
    pass

class InvestigationResponse(InvestigationBase):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
