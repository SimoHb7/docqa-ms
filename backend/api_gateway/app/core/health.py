"""
Health check endpoints for DocQA-MS API Gateway
"""
from datetime import datetime
from typing import Dict, Any
import asyncio
import httpx
from fastapi import APIRouter, HTTPException
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


async def check_service(url: str, service_name: str) -> Dict[str, Any]:
    """Check microservice health"""
    try:
        async with httpx.AsyncClient(timeout=settings.HEALTH_CHECK_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                return {"status": "healthy", "message": f"{service_name} is responding"}
            else:
                return {"status": "unhealthy", "message": f"{service_name} returned status {response.status_code}"}
    except Exception as e:
        logger.error(f"{service_name} health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"{service_name} connection failed: {str(e)}"}


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for all system components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "api-gateway",
        "checks": {}
    }

    # Check database
    health_status["checks"]["database"] = await check_database()

    # Check message queue
    health_status["checks"]["rabbitmq"] = await check_rabbitmq()

    # Check microservices
    services_to_check = [
        ("http://doc-ingestor:8001", "doc-ingestor"),
        ("http://deid:8002", "deid"),
        ("http://indexer-semantique:8003", "indexer-semantique"),
        ("http://llm-qa:8004", "llm-qa"),
        ("http://synthese-comparative:8005", "synthese-comparative"),
    ]

    # Run all service checks concurrently
    service_checks = await asyncio.gather(
        *[check_service(url, name) for url, name in services_to_check],
        return_exceptions=True
    )

    for i, (url, name) in enumerate(services_to_check):
        if isinstance(service_checks[i], Exception):
            health_status["checks"][name] = {
                "status": "unhealthy",
                "message": f"Health check failed: {str(service_checks[i])}"
            }
        else:
            health_status["checks"][name] = service_checks[i]

    # Determine overall health status
    all_checks = list(health_status["checks"].values())
    if any(check.get("status") == "unhealthy" for check in all_checks):
        health_status["status"] = "degraded"
    elif all(check.get("status") == "healthy" for check in all_checks):
        health_status["status"] = "healthy"
    else:
        health_status["status"] = "unknown"

    # Return appropriate HTTP status
    if health_status["status"] == "healthy":
        return health_status
    elif health_status["status"] == "degraded":
        # Return 200 but indicate degraded status
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)


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
            "message": "API Gateway is ready to accept requests"
        }
    else:
        raise HTTPException(
            status_code=503,
            detail="API Gateway is not ready"
        )


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - ensures the service is running
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API Gateway is running"
    }