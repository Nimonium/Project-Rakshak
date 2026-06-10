import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog
import uuid

from backend.app.api.router import api_router, ws_router
from backend.app.core.config import settings
from backend.app.core.websocket_manager import manager
from backend.app.services.scoring_service import global_graph_builder
from backend.app.db.session import async_session_maker
from backend.app.db.models.transaction import Transaction
from sqlalchemy.future import select

# Configure basic structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Load models, connect to DB, connect to Redis
    logger.info("Starting up Project Rakshak Backend")
    
    # Pre-populate GraphBuilder from DB
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(Transaction))
            txs = result.scalars().all()
            for tx in txs:
                if tx.sender_account_id and tx.receiver_account_id:
                    global_graph_builder.add_transaction(
                        sender_id=tx.sender_account_id,
                        receiver_id=tx.receiver_account_id,
                        amount=tx.amount,
                        tx_id=tx.id
                    )
            logger.info(f"Populated GraphBuilder with {len(txs)} transactions.")
    except Exception as e:
        logger.error(f"Failed to populate GraphBuilder: {str(e)}")

    yield
    # Shutdown logic: Close connections, cleanup resources
    logger.info("Shutting down Project Rakshak Backend")

app = FastAPI(
    title="Project Rakshak",
    description="Enterprise-grade banking fraud intelligence platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Configuration
origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = str(uuid.uuid4())
    structlog.threadlocal.clear_threadlocal()
    structlog.threadlocal.bind_threadlocal(request_id=req_id, path=request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

# Health Check Route
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "rakshak-backend"}

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)
