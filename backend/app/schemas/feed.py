from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RegulatoryFeedBase(BaseModel):
    source: str
    entity_type: str
    entity_value: str
    risk_weight: float

class RegulatoryFeedCreate(RegulatoryFeedBase):
    pass

class RegulatoryFeedResponse(RegulatoryFeedBase):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
