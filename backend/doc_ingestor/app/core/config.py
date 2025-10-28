"""
Configuration settings for DocQA-MS Document Ingestor
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    ALLOWED_HOSTS: List[str] = ["*"]

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
    ]

    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/docqa_db"

    # Message queue settings
    RABBITMQ_URL: str = "amqp://admin:admin@localhost:5672/"

    # File processing settings
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50  # Increased from 10MB to 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        # Primary document formats
        "pdf", "docx", "doc", "txt",
        # Medical standard formats
        "hl7", "fhir", "json", "xml",
        # Additional document formats
        "rtf", "odt",
        # Spreadsheets (for lab results, etc.)
        "xlsx", "xls", "csv", "ods",
        # Presentations
        "pptx", "ppt", "odp",
        # Images (for OCR)
        "png", "jpg", "jpeg", "tiff", "tif", "bmp", "gif",
        # Medical imaging formats
        "dcm", "dicom",
        # Other text formats
        "html", "htm", "md", "markdown", "rst"
    ]

    # OCR settings
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"

    # Health check settings
    HEALTH_CHECK_TIMEOUT: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
