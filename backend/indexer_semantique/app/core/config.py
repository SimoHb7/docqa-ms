"""
Configuration settings for Semantic Indexer service
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Service Configuration
    SERVICE_NAME: str = "indexer-semantique"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Message Queue Configuration
    RABBITMQ_URL: str = Field(..., env="RABBITMQ_URL")
    QUEUE_NAME: str = "document_indexing"

    # Embedding Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    MAX_SEQ_LENGTH: int = 512
    BATCH_SIZE: int = 32
    DEVICE: str = "cpu"  # 'cpu' or 'cuda'

    # Text Chunking Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_LENGTH: int = 50

    # FAISS Configuration
    VECTOR_INDEX_PATH: str = "/app/data/vectors/faiss_index.idx"
    VECTOR_METADATA_PATH: str = "/app/data/vectors/metadata.json"
    SIMILARITY_THRESHOLD: float = 0.7

    # Search Configuration
    MAX_SEARCH_RESULTS: int = 20
    SEARCH_TIMEOUT: int = 30  # seconds

    # Performance Configuration
    MAX_WORKERS: int = 4
    CACHE_SIZE: int = 1000
    MEMORY_LIMIT: str = "2GB"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()