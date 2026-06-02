import asyncio
from backend.app.db.session import engine
from backend.app.db.base import Base
from backend.app.db.models import *

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tables created successfully")

asyncio.run(init_db())
