"""Application configuration."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App
    APP_NAME: str = "WavyAI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://wavyai:wavyai_password@localhost:5432/wavyai"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "wavyai"
    POSTGRES_USER: str = "wavyai"
    POSTGRES_PASSWORD: str = "wavyai_password"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # ARGO Data
    ARGO_DATA_PATH: str = "data/raw"

    # LLM / Embeddings
    GOOGLE_GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_MAX_TOKENS: int = 2048

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Rate Limiting
    RATE_LIMIT_PER_HOUR: int = 100

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@wavyai.com"

    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

    @property
    def database_url_async(self) -> str:
        """Get asynchronous database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

