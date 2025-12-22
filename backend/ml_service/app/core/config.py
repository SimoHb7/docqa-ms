"""
ML Service Configuration
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """ML Service Settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DocQA-MS ML Service"
    VERSION: str = "1.0.0"
    
    # Server Configuration
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@postgres:5432/docqa_db"
    
    # RabbitMQ Configuration
    RABBITMQ_URL: str = "amqp://admin:admin@rabbitmq:5672/"
    
    # Model Configuration
    MODEL_DIR: str = "./saved_models"
    DATA_DIR: str = "./data"
    
    # Document Classifier Settings
    CLASSIFIER_MODEL_PATH: str = "./saved_models/document_classifier_model"
    CLASSIFIER_USE_PRETRAINED: bool = False  # Use pre-trained or custom trained
    CLASSIFIER_PRETRAINED_MODEL: str = "camembert-base"
    
    # Medical NER Settings
    NER_MODEL_PATH: str = "./saved_models/medical_ner_model"
    NER_USE_PRETRAINED: bool = False
    NER_PRETRAINED_MODEL: str = "dmis-lab/biobert-v1.1"
    
    # Risk Predictor Settings
    RISK_MODEL_PATH: str = "./saved_models/risk_predictor"
    
    # Inference Settings
    MAX_BATCH_SIZE: int = 32
    MAX_SEQUENCE_LENGTH: int = 512
    DEVICE: str = "cpu"  # or "cuda" if GPU available
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
