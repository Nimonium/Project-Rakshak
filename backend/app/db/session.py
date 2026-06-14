from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL query logging
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
