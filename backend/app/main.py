"""FastAPI приложение AutoAI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.http_client import close_http_client
from app.api.v1 import cars, search, ai_analysis, parsers
from app.core.logger import setup_logger

logger = setup_logger(__name__)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: startup и shutdown"""
    # Startup
    await create_tables()
    logger.info("🚀 Приложение запущено")
    yield
    # Shutdown
    await close_http_client()
    await engine.dispose()
    logger.info("🛑 Приложение остановлено")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.3.0",
    description="AI-powered car listing analyzer",
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты
app.include_router(cars.router, prefix="/api/v1/cars", tags=["cars"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(ai_analysis.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(parsers.router, prefix="/api/v1/parsers", tags=["parsers"])


@app.get("/")
async def root():
    return {
        "message": "AutoAI API",
        "version": "0.3.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.3.0"}


@app.get("/ready")
async def readiness():
    """Readiness probe — проверяет зависимости"""
    from sqlalchemy import text
    from app.core.database import async_session
    import redis.asyncio as aioredis
    
    checks = {"postgres": False, "redis": False}
    
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            checks["postgres"] = True
    except Exception as e:
        logger.error(f"Postgres not ready: {e}")
    
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis not ready: {e}")
    
    all_ok = all(checks.values())
    
    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks
    }, 200 if all_ok else 503


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
