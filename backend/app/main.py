from app.api.v1 import ai_analysis, cars, parsers, search
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="AutoAI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars.router, prefix="/api/v1/cars", tags=["cars"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(ai_analysis.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(parsers.router, prefix="/api/v1/parsers", tags=["parsers"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
async def root():
    return {"message": "AutoAI API", "docs": "/docs", "health": "/health"}
