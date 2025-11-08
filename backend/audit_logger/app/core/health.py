"""
Health check endpoints for DocQA-MS Audit Logger
"""
import time
from typing import Dict, Any
import psycopg2
from fastapi import APIRouter, HTTPException
import structlog

from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)


def check_database() -> Dict[str, Any]:
    """Check database connectivity"""
    try:
        conn = psycopg2.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            connect_timeout=settings.HEALTH_CHECK_TIMEOUT,
        )
        conn.close()
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "service": "audit-logger"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with all dependencies"""
    checks = {
        "database": check_database(),
    }

    # Determine overall status
    overall_status = "healthy"
    for check_name, check_result in checks.items():
        if check_result["status"] == "unhealthy":
            overall_status = "degraded"
            break

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "version": "1.0.0",
        "service": "audit-logger",
        "checks": checks
    }