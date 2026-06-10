import asyncio
from backend.app.db.base import Base
from backend.app.db.session import engine
import backend.app.db.models

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")

asyncio.run(main())
