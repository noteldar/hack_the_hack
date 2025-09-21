"""
Configuration settings for MeetingAssassin
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MeetingAssassin"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./meeting_assassin.db"

    # Google Calendar API
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # OpenAI API (for AI features)
    OPENAI_API_KEY: Optional[str] = None

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Origins
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Redis (optional for caching)
    REDIS_URL: Optional[str] = None

    # Avatar personalities
    DEFAULT_AVATAR_PERSONALITY: str = "professional"

    # Genetic algorithm parameters
    POPULATION_SIZE: int = 50
    MUTATION_RATE: float = 0.1
    CROSSOVER_RATE: float = 0.8
    MAX_GENERATIONS: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()