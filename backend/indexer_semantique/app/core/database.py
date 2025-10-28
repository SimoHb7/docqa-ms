"""
Database operations for Semantic Indexer service
"""
import asyncpg
import json
from typing import List, Dict, Any, Optional
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
    
    async def save_document_chunk(
        self,
        document_id: str,
        chunk_index: int,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save a document chunk to the database
        
        Returns the chunk ID (UUID)
        """
        try:
            async with self.pool.acquire() as conn:
                # Check if document exists, if not create placeholder
                doc_exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM documents WHERE id = $1)",
                    document_id
                )
                
                if not doc_exists:
                    # Create minimal document record
                    await conn.execute(
                        """
                        INSERT INTO documents (id, filename, file_type, content, processing_status)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        document_id,
                        metadata.get('title', 'Unknown'),
                        metadata.get('file_type', 'txt'),
                        '',  # Content will be built from chunks
                        'indexed'
                    )
                
                # Insert or update chunk
                chunk_id = await conn.fetchval(
                    """
                    INSERT INTO document_chunks (document_id, chunk_index, content, metadata)
                    VALUES ($1, $2, $3, $4::jsonb)
                    ON CONFLICT (document_id, chunk_index) 
                    DO UPDATE SET content = $3, metadata = $4::jsonb, created_at = now()
                    RETURNING id
                    """,
                    document_id,
                    chunk_index,
                    content,
                    json.dumps(metadata)
                )
                
                logger.debug("Saved document chunk",
                           document_id=document_id,
                           chunk_index=chunk_index,
                           chunk_id=str(chunk_id))
                
                return str(chunk_id)
                
        except Exception as e:
            logger.error("Failed to save document chunk",
                        document_id=document_id,
                        chunk_index=chunk_index,
                        error=str(e))
            raise
    
    async def get_document_chunks(
        self,
        document_id: str
    ) -> List[Dict[str, Any]]:
        """Get all chunks for a document"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, chunk_index, content, metadata, created_at
                    FROM document_chunks
                    WHERE document_id = $1
                    ORDER BY chunk_index
                    """,
                    document_id
                )
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error("Failed to get document chunks",
                        document_id=document_id,
                        error=str(e))
            return []
    
    async def delete_document_chunks(self, document_id: str) -> int:
        """Delete all chunks for a document"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM document_chunks WHERE document_id = $1",
                    document_id
                )
                
                # Extract count from result string like "DELETE 5"
                count = int(result.split()[-1]) if result else 0
                
                logger.info("Deleted document chunks",
                           document_id=document_id,
                           count=count)
                
                return count
                
        except Exception as e:
            logger.error("Failed to delete document chunks",
                        document_id=document_id,
                        error=str(e))
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            async with self.pool.acquire() as conn:
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(DISTINCT document_id) as total_documents,
                        COUNT(*) as total_chunks
                    FROM document_chunks
                    """
                )
                
                return {
                    "total_documents": stats['total_documents'],
                    "total_chunks": stats['total_chunks']
                }
                
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {"total_documents": 0, "total_chunks": 0}


# Global database manager instance
db_manager = DatabaseManager()
