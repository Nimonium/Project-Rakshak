import structlog
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.regulatory_feed import RegulatoryFeed

logger = structlog.get_logger(__name__)

class FeedIngestionService:
    def __init__(self):
        # Mock external APIs for demonstration
        self.sources = ["RBI", "CERT-In", "NCRP"]
        
        # In-memory cache for fast lookups during scoring
        self.blacklist_cache = set()

    async def fetch_and_ingest_feeds(self, session: AsyncSession):
        """Simulates fetching from external regulatory feeds and saving to DB."""
        logger.info("Fetching regulatory feeds...")
        
        mock_feeds = [
            {"source": "RBI", "entity_type": "ACCOUNT", "entity_value": "ACCT-9999", "risk_weight": 1.0},
            {"source": "CERT-In", "entity_type": "IP", "entity_value": "192.168.1.100", "risk_weight": 0.8},
            {"source": "NCRP", "entity_type": "DEVICE", "entity_value": "DEV-BAD-01", "risk_weight": 0.9},
        ]
        
        for feed in mock_feeds:
            # Check if exists
            # For simplicity, we just add to cache here. In reality, query DB first.
            self.blacklist_cache.add(feed["entity_value"])
            
            db_feed = RegulatoryFeed(
                source=feed["source"],
                entity_type=feed["entity_type"],
                entity_value=feed["entity_value"],
                risk_weight=feed["risk_weight"]
            )
            session.add(db_feed)
            
        await session.commit()
        logger.info("Regulatory feeds ingested successfully.")

    def is_blacklisted(self, entity_value: str) -> bool:
        """Fast lookup during real-time scoring."""
        return entity_value in self.blacklist_cache

feed_service = FeedIngestionService()
