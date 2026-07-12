from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "AutoAI"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://autoai:autoai@postgres:5432/autoai"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # API Security
    API_KEY: str = "change-me-in-production"
    
    # Apify
    APIFY_TOKEN: str = ""
    
    # ScraperAPI (альтернатива)
    SCRAPERAPI_KEY: str = ""
    
    # YandexGPT (опционально)
    YANDEX_GPT_API_KEY: str = ""
    YC_FOLDER_ID: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
