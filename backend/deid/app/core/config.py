"""
Configuration settings for DocQA-MS DeID Service
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Service Configuration
    SERVICE_NAME: str = "deid"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8002, env="PORT")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/docqa_db",
        env="DATABASE_URL"
    )

    # Message Queue Configuration
    RABBITMQ_URL: str = Field(
        default="amqp://admin:admin@localhost:5672/",
        env="RABBITMQ_URL"
    )

    # DeID Configuration
    DEID_MODEL_PATH: str = Field(default="/app/models", env="DEID_MODEL_PATH")
    DEID_LANGUAGE: str = Field(default="fr", env="DEID_LANGUAGE")
    DEID_CONFIDENCE_THRESHOLD: float = Field(default=0.5, env="DEID_CONFIDENCE_THRESHOLD")

    # SpaCy Configuration
    SPACY_MODEL: str = Field(default="fr_core_news_sm", env="SPACY_MODEL")

    # Presidio Configuration
    # Note: IBAN_CODE recognizer is not available for French language
    PRESIDIO_ANALYZERS: list = Field(
        default=["PERSON", "LOCATION", "DATE_TIME", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD"],
        env="PRESIDIO_ANALYZERS"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT: float = Field(default=10.0, env="HEALTH_CHECK_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()