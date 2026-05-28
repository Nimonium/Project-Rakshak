import asyncio
import json
import structlog
import redis.asyncio as aioredis
from backend.app.core.config import settings
from backend.app.core.websocket_manager import manager

logger = structlog.get_logger(__name__)

class RedisPubSubManager:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.pubsub = None
        self.redis = None

    async def connect(self):
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            self.pubsub = self.redis.pubsub()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")

    async def subscribe_and_listen(self, channel: str = "transactions"):
        """Subscribes to a Redis channel and broadcasts messages to WebSockets."""
        if not self.pubsub:
            await self.connect()
            
        if not self.pubsub:
            logger.error("Could not initialize Redis Pub/Sub.")
            return

        await self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to Redis channel: {channel}")
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"].decode("utf-8"))
                    # Broadcast to all connected WebSocket clients
                    await manager.broadcast(data)
        except asyncio.CancelledError:
            logger.info("Redis listener task cancelled.")
        except Exception as e:
            logger.error(f"Error in Redis listener: {str(e)}")
        finally:
            if self.pubsub:
                await self.pubsub.unsubscribe(channel)

    async def publish(self, channel: str, message: dict):
        """Publishes a message to a Redis channel."""
        if not self.redis:
            await self.connect()
        
        if self.redis:
            await self.redis.publish(channel, json.dumps(message))

redis_pubsub = RedisPubSubManager()
