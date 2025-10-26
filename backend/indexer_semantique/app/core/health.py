"""
Health check utilities for Semantic Indexer service
"""
from typing import Dict, Any
from app.core.config import settings
from app.core.logging import get_logger
from app.core.embeddings import embedding_service
from app.core.vector_store import vector_store

logger = get_logger(__name__)


def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Will be set by FastAPI
            "version": settings.VERSION,
            "service": settings.SERVICE_NAME,
            "checks": {}
        }

        # Check embedding service
        try:
            embedding_info = embedding_service.get_model_info()
            health_data["checks"]["embedding_service"] = {
                "status": "healthy",
                "message": "Embedding model ready",
                "model": embedding_info.get("model_name", "unknown"),
                "device": embedding_info.get("device", "unknown")
            }
        except Exception as e:
            health_data["checks"]["embedding_service"] = {
                "status": "unhealthy",
                "message": f"Embedding service failed: {str(e)}"
            }
            health_data["status"] = "degraded"

        # Check vector store
        try:
            vector_stats = vector_store.get_stats()
            health_data["checks"]["vector_store"] = {
                "status": "healthy",
                "message": "Vector store operational",
                "total_vectors": vector_stats.get("total_vectors", 0),
                "total_chunks": vector_stats.get("total_chunks", 0),
                "dimension": vector_stats.get("dimension", 0)
            }
        except Exception as e:
            health_data["checks"]["vector_store"] = {
                "status": "unhealthy",
                "message": f"Vector store failed: {str(e)}"
            }
            health_data["status"] = "degraded"

        # Check configuration
        health_data["checks"]["configuration"] = {
            "status": "healthy",
            "message": "Configuration loaded",
            "embedding_model": settings.EMBEDDING_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "batch_size": settings.BATCH_SIZE
        }

        # Overall status
        if health_data["status"] == "healthy":
            logger.debug("Health check passed", checks=len(health_data["checks"]))
        else:
            logger.warning("Health check failed", status=health_data["status"])

        return health_data

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": settings.VERSION,
            "service": settings.SERVICE_NAME,
            "error": str(e),
            "checks": {}
        }


def is_service_healthy() -> bool:
    """Quick health check for service availability"""
    try:
        health = get_health_status()
        return health.get("status") == "healthy"
    except Exception:
        return False