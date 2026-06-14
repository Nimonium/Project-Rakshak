from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from backend.app.api import deps
from backend.app.schemas.feed import RegulatoryFeedResponse
from backend.app.db.models.regulatory_feed import RegulatoryFeed

router = APIRouter()

@router.get("/", response_model=List[RegulatoryFeedResponse])
async def get_feeds(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(deps.get_db)
):
    result = await db.execute(
        select(RegulatoryFeed).order_by(RegulatoryFeed.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/sync", response_model=List[RegulatoryFeedResponse])
async def sync_feeds(
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Simulates fetching new regulatory feeds.
    In a real system, this would call external APIs.
    """
    # Create some mock feeds to simulate the sync
    mock_feeds = [
        RegulatoryFeed(source="RBI", entity_type="ACCOUNT", entity_value="MOCK-ACC-1", risk_weight=0.9),
        RegulatoryFeed(source="CERT-In", entity_type="IP", entity_value="192.168.1.1", risk_weight=0.8)
    ]
    for feed in mock_feeds:
        db.add(feed)
    await db.commit()
    for feed in mock_feeds:
        await db.refresh(feed)
    
    result = await db.execute(
        select(RegulatoryFeed).order_by(RegulatoryFeed.created_at.desc()).limit(10)
    )
    return result.scalars().all()
