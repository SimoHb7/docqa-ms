"""
Database service for Synthese Comparative
Handles connections to PostgreSQL and queries for anonymized documents
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Global engine instance
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """
    Get or create database engine with connection pooling
    """
    global _engine
    
    if _engine is None:
        logger.info("Creating database engine", database_url=settings.DATABASE_URL)
        _engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=settings.DEBUG,
        )
        logger.info("Database engine created successfully")
    
    return _engine


def get_connection():
    """
    Get a database connection from the pool
    """
    engine = get_engine()
    return engine.connect()


async def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch document metadata by ID
    
    Args:
        document_id: UUID of the document
        
    Returns:
        Document metadata or None if not found
    """
    try:
        with get_connection() as conn:
            result = conn.execute(
                text("""
                    SELECT id, filename, file_type, content, 
                           processing_status, is_anonymized, 
                           metadata, created_at
                    FROM documents
                    WHERE id = :document_id
                """),
                {"document_id": document_id}
            )
            row = result.fetchone()
            
            if row:
                return {
                    "id": str(row[0]),
                    "filename": row[1],
                    "file_type": row[2],
                    "content": row[3],
                    "processing_status": row[4],
                    "is_anonymized": row[5],
                    "metadata": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                }
            
            return None
            
    except Exception as e:
        logger.error("Failed to fetch document", document_id=document_id, error=str(e))
        raise


async def get_anonymized_content(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch anonymized content for a document
    
    Args:
        document_id: UUID of the document
        
    Returns:
        Anonymized content with PII entities or None if not found
    """
    try:
        with get_connection() as conn:
            result = conn.execute(
                text("""
                    SELECT id, document_id, anonymized_content, 
                           pii_entities, processing_time_ms, created_at
                    FROM document_anonymizations
                    WHERE document_id = :document_id
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"document_id": document_id}
            )
            row = result.fetchone()
            
            if row:
                return {
                    "id": str(row[0]),
                    "document_id": row[1],
                    "anonymized_content": row[2],
                    "pii_entities": row[3],
                    "processing_time_ms": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                }
            
            return None
            
    except Exception as e:
        logger.error("Failed to fetch anonymized content", document_id=document_id, error=str(e))
        raise


async def get_multiple_documents(document_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch multiple documents by IDs
    
    Args:
        document_ids: List of document UUIDs
        
    Returns:
        List of document metadata dictionaries
    """
    try:
        if not document_ids:
            return []
        
        with get_connection() as conn:
            # Convert list to PostgreSQL array format
            placeholders = ", ".join([f":id_{i}" for i in range(len(document_ids))])
            params = {f"id_{i}": doc_id for i, doc_id in enumerate(document_ids)}
            
            result = conn.execute(
                text(f"""
                    SELECT id, filename, file_type, content, 
                           processing_status, is_anonymized, 
                           metadata, created_at
                    FROM documents
                    WHERE id::text IN ({placeholders})
                    ORDER BY created_at DESC
                """),
                params
            )
            
            documents = []
            for row in result:
                documents.append({
                    "id": str(row[0]),
                    "filename": row[1],
                    "file_type": row[2],
                    "content": row[3],
                    "processing_status": row[4],
                    "is_anonymized": row[5],
                    "metadata": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                })
            
            return documents
            
    except Exception as e:
        logger.error("Failed to fetch multiple documents", error=str(e))
        raise


async def get_multiple_anonymized_contents(document_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch anonymized content for multiple documents
    
    Args:
        document_ids: List of document UUIDs
        
    Returns:
        List of anonymized content dictionaries
    """
    try:
        if not document_ids:
            return []
        
        with get_connection() as conn:
            # Create a subquery to get the latest anonymization for each document
            placeholders = ", ".join([f":id_{i}" for i in range(len(document_ids))])
            params = {f"id_{i}": doc_id for i, doc_id in enumerate(document_ids)}
            
            result = conn.execute(
                text(f"""
                    SELECT DISTINCT ON (document_id)
                           id, document_id, anonymized_content, 
                           pii_entities, processing_time_ms, created_at
                    FROM document_anonymizations
                    WHERE document_id IN ({placeholders})
                    ORDER BY document_id, created_at DESC
                """),
                params
            )
            
            anonymizations = []
            for row in result:
                anonymizations.append({
                    "id": str(row[0]),
                    "document_id": row[1],
                    "anonymized_content": row[2],
                    "pii_entities": row[3],
                    "processing_time_ms": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                })
            
            return anonymizations
            
    except Exception as e:
        logger.error("Failed to fetch multiple anonymized contents", error=str(e))
        raise


async def test_connection() -> bool:
    """
    Test database connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False
