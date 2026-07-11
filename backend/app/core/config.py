from typing import List

from pydantic_settings import BaseSettings


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

    # YandexGPT (опционально)
    YANDEX_GPT_API_KEY: str = ""
    YC_FOLDER_ID: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
