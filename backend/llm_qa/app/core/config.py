"""
Configuration for LLM QA Service
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # API Configuration
    API_V1_STR: str = "/api/v1"

    # Groq API Configuration
    GROQ_API_KEY: str = "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"
    GROQ_MODEL: str = "llama-3.1-70b-versatile"  # Current available model for medical Q&A

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@postgres:5432/docqa_db"

    # Message Queue Configuration
    RABBITMQ_URL: str = "amqp://admin:admin@rabbitmq:5672/"

    # External Services
    INDEXER_URL: str = "http://indexer-semantique:8003"

    # Service Configuration
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8004

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Q&A Configuration
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1000
    MAX_CONTEXT_CHUNKS: int = 5  # Limit context to avoid token limits

    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()