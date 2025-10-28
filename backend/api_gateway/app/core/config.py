"""
Core configuration for DocQA-MS API Gateway
"""
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server Configuration
    SERVER_NAME: str = "DocQA-MS API Gateway"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    DEBUG: bool = True

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # API Gateway
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/docqa_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "user"
    DATABASE_PASSWORD: str = "password"
    DATABASE_NAME: str = "docqa_db"

    # Message Queue Configuration
    RABBITMQ_URL: str = "amqp://admin:admin@localhost:5672/"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin"
    RABBITMQ_VHOST: str = "/"

    # Service URLs (for routing to microservices)
    DOC_INGESTOR_URL: str = "http://localhost:8001"
    DEID_URL: str = "http://localhost:8002"
    INDEXER_SEMANTIQUE_URL: str = "http://localhost:8003"
    LLM_QA_URL: str = "http://localhost:8004"
    SYNTHESE_COMPARATIVE_URL: str = "http://localhost:8005"
    AUDIT_LOGGER_URL: str = "http://localhost:8006"

    # File Upload Configuration
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "hl7", "fhir"]
    UPLOAD_DIR: str = "./data/uploads"

    # Security Configuration
    ENCRYPTION_KEY: str = "your-32-character-encryption-key"
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090

    # Cache Configuration (optional)
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT: int = 10  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()