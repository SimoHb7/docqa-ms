"""
Health check endpoints for Synthese Comparative Service
"""
from datetime import datetime
from typing import Dict, Any
import asyncio
import httpx
from fastapi import APIRouter
import psycopg2
import pika

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


async def check_database() -> Dict[str, Any]:
    """Check database connectivity"""
    try:
        # Use DATABASE_URL for Docker container networking
        conn = psycopg2.connect(
            settings.DATABASE_URL,
            connect_timeout=5
        )
        conn.close()
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}


async def check_rabbitmq() -> Dict[str, Any]:
    """Check RabbitMQ connectivity"""
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.RABBITMQ_URL)
        )
        connection.close()
        return {"status": "healthy", "message": "RabbitMQ connection successful"}
    except Exception as e:
        logger.error("RabbitMQ health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"RabbitMQ connection failed: {str(e)}"}


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for the Synthese Comparative service
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "synthese-comparative",
        "checks": {}
    }

    # Check database
    health_status["checks"]["database"] = await check_database()

    # Check message queue
    health_status["checks"]["rabbitmq"] = await check_rabbitmq()

    # Determine overall health status
    all_checks = list(health_status["checks"].values())
    if any(check.get("status") == "unhealthy" for check in all_checks):
        health_status["status"] = "degraded"
    elif all(check.get("status") == "healthy" for check in all_checks):
        health_status["status"] = "healthy"
    else:
        health_status["status"] = "unknown"

    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - ensures the service is ready to accept traffic
    """
    # Basic readiness checks (database and message queue)
    db_check = await check_database()
    mq_check = await check_rabbitmq()

    if db_check["status"] == "healthy" and mq_check["status"] == "healthy":
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Synthese Comparative service is ready to accept requests"
        }
    else:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Synthese Comparative service is not ready"
        }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - ensures the service is running
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Synthese Comparative service is running"
    }