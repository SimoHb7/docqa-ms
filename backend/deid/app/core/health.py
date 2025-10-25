"""
Health check utilities for DeID service
"""
from datetime import datetime
from typing import Dict, Any
import psycopg2
import pika

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

async def check_database() -> Dict[str, Any]:
    """Check database connectivity"""
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.close()
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}

async def check_rabbitmq() -> Dict[str, Any]:
    """Check RabbitMQ connectivity"""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        connection.close()
        return {"status": "healthy", "message": "RabbitMQ connection successful"}
    except Exception as e:
        logger.error("RabbitMQ health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"RabbitMQ connection failed: {str(e)}"}

async def check_spacy_model() -> Dict[str, Any]:
    """Check if spaCy model is loaded"""
    try:
        import spacy
        nlp = spacy.load(settings.SPACY_MODEL)
        return {"status": "healthy", "message": f"spaCy model {settings.SPACY_MODEL} loaded"}
    except Exception as e:
        logger.error("spaCy model health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"spaCy model failed: {str(e)}"}

async def check_presidio() -> Dict[str, Any]:
    """Check if Presidio is working"""
    try:
        from presidio_analyzer import AnalyzerEngine
        analyzer = AnalyzerEngine()
        return {"status": "healthy", "message": "Presidio analyzer initialized"}
    except Exception as e:
        logger.error("Presidio health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"Presidio failed: {str(e)}"}