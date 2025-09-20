from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import secrets
import os


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Delegate.ai"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str
    DATABASE_TEST_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CELERY_URL: Optional[str] = None

    @validator("REDIS_CELERY_URL", pre=True, always=True)
    def set_redis_celery_url(cls, v, values):
        if v is None:
            return values.get("REDIS_URL", "redis://localhost:6379/0")
        return v

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None

    # API Keys
    OPENAI_API_KEY: Optional[str] = None

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @validator("CELERY_BROKER_URL", pre=True, always=True)
    def set_celery_broker_url(cls, v, values):
        if v is None:
            return values.get("REDIS_CELERY_URL") or values.get("REDIS_URL", "redis://localhost:6379/0")
        return v

    @validator("CELERY_RESULT_BACKEND", pre=True, always=True)
    def set_celery_result_backend(cls, v, values):
        if v is None:
            return values.get("REDIS_CELERY_URL") or values.get("REDIS_URL", "redis://localhost:6379/0")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()