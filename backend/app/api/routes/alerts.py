from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from backend.app.api import deps
from backend.app.schemas.alert import AlertResponse
from backend.app.db.models.alert import Alert

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Returns active alerts.
    """
    result = await db.execute(
        select(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit)
    )
    alerts = result.scalars().all()
    return alerts
