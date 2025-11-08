"""
Database operations for Document Ingestor service
"""
import asyncpg
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection and operations manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to create database pool", error=str(e))
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def save_document(
        self,
        document_id: str,
        filename: str,
        file_type: str,
        content: str,
        file_size: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a document to the database
        
        Returns the document ID
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO documents 
                    (id, filename, file_type, content, file_size, processing_status, 
                     is_anonymized, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                    ON CONFLICT (id) DO UPDATE 
                    SET filename = $2, file_type = $3, content = $4, 
                        file_size = $5, metadata = $8::jsonb
                    """,
                    document_id,
                    filename,
                    file_type,
                    content,
                    file_size,
                    'uploaded',  # processing_status
                    False,       # is_anonymized
                    json.dumps(metadata) if metadata else '{}'
                )
                
                logger.info("Document saved to database",
                           document_id=document_id,
                           filename=filename,
                           file_type=file_type,
                           size=file_size)
                
                return document_id
                
        except Exception as e:
            logger.error("Failed to save document",
                        document_id=document_id,
                        error=str(e))
            raise
    
    async def update_document_status(
        self,
        document_id: str,
        status: str
    ) -> None:
        """Update document processing status"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE documents 
                    SET processing_status = $1
                    WHERE id = $2
                    """,
                    status,
                    document_id
                )
                
                logger.info("Document status updated",
                           document_id=document_id,
                           status=status)
                
        except Exception as e:
            logger.error("Failed to update document status",
                        document_id=document_id,
                        error=str(e))
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT id, filename, file_type, content, file_size,
                           processing_status, is_anonymized, metadata, 
                           upload_date, created_at
                    FROM documents
                    WHERE id = $1
                    """,
                    document_id
                )
                
                return dict(row) if row else None
                
        except Exception as e:
            logger.error("Failed to get document",
                        document_id=document_id,
                        error=str(e))
            return None
    
    async def list_documents(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """List documents with pagination"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, filename, file_type, file_size,
                           processing_status, is_anonymized, upload_date
                    FROM documents
                    ORDER BY upload_date DESC
                    LIMIT $1 OFFSET $2
                    """,
                    limit,
                    offset
                )
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error("Failed to list documents", error=str(e))
            return []


# Global database manager instance
db_manager = DatabaseManager()
