"""FastAPI приложение AutoAI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.v1 import cars, search, ai_analysis, parsers
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Создаём таблицы при старте
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Создаём приложение
app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    description="AI-powered car listing analyzer",
)

# Подключаем rate limiter
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

@app.on_event("startup")
async def startup():
    """Действия при запуске"""
    await create_tables()
    logger.info("🚀 Приложение запущено")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "AutoAI API",
        "version": "0.2.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "version": "0.2.0"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )
